"""
RAG (Retrieval-Augmented Generation) System for Study Assistant.

This module provides:
1. Content indexing from notes, flashcards, and past papers
2. BM25 keyword-based retrieval (always available)
3. Optional semantic search using sentence-transformers
4. Context formatting for Claude API

The RAG system helps the AI give more relevant answers by searching
through your study materials first.
"""

import sqlite3
import math
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Optional, Tuple

# Database path (same as main database)
DATABASE_PATH = Path(__file__).parent / "study.db"

# Semantic search status tracking
SEMANTIC_STATUS = {
    'available': False,
    'error': None,
    'model_name': 'all-MiniLM-L6-v2',
    'model_loaded': False
}

# Try to import sentence-transformers for semantic search
SEMANTIC_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SEMANTIC_AVAILABLE = True
    SEMANTIC_STATUS['available'] = True
except ImportError as e:
    SEMANTIC_STATUS['error'] = f"sentence-transformers not installed: {e}"
except Exception as e:
    SEMANTIC_STATUS['error'] = f"Failed to load semantic search: {e}"


def get_semantic_status() -> Dict:
    """Get detailed status of semantic search capability."""
    status = SEMANTIC_STATUS.copy()
    if SEMANTIC_AVAILABLE:
        # Check if model is loaded
        status['model_loaded'] = _embedding_model is not None
    return status


# =============================================================================
# DATABASE SETUP
# =============================================================================

def init_rag_database():
    """Create RAG-specific tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Document chunks table - stores indexed content
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT NOT NULL,
            source_id INTEGER NOT NULL,
            subject_id INTEGER,
            title TEXT,
            content TEXT NOT NULL,
            tokens TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source_type, source_id)
        )
    """)

    # BM25 statistics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total_docs INTEGER DEFAULT 0,
            avg_doc_length REAL DEFAULT 0,
            doc_frequencies TEXT DEFAULT '{}',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert default stats row if not exists
    cursor.execute("""
        INSERT OR IGNORE INTO rag_stats (id, total_docs, avg_doc_length, doc_frequencies)
        VALUES (1, 0, 0, '{}')
    """)

    conn.commit()
    conn.close()


def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# TEXT PROCESSING
# =============================================================================

def tokenize(text: str) -> List[str]:
    """
    Simple tokenizer that splits text into lowercase words.
    Removes punctuation and common stop words.
    """
    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
        'they', 'what', 'which', 'who', 'whom', 'where', 'when', 'why', 'how',
        'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just'
    }

    # Convert to lowercase and split on non-alphanumeric characters
    words = re.findall(r'[a-z0-9]+', text.lower())

    # Remove stop words and short words
    tokens = [w for w in words if w not in STOP_WORDS and len(w) > 2]

    return tokens


def chunk_text(text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split long text into overlapping chunks.
    Tries to split on sentence boundaries.
    """
    if len(text) <= max_chunk_size:
        return [text]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


# =============================================================================
# BM25 IMPLEMENTATION
# =============================================================================

class BM25:
    """
    BM25 (Best Matching 25) ranking algorithm.
    A proven information retrieval algorithm used by search engines.

    BM25 scores documents based on:
    - Term frequency (how often query terms appear in document)
    - Inverse document frequency (rare terms are more important)
    - Document length normalization
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 parameters.

        Args:
            k1: Term frequency saturation parameter (default 1.5)
            b: Document length normalization (0-1, default 0.75)
        """
        self.k1 = k1
        self.b = b

    def score(self, query_tokens: List[str], doc_tokens: List[str],
              doc_frequencies: Dict[str, int], total_docs: int,
              avg_doc_length: float) -> float:
        """
        Calculate BM25 score for a document given a query.

        Args:
            query_tokens: Tokenized query
            doc_tokens: Tokenized document
            doc_frequencies: Dict mapping terms to document count
            total_docs: Total number of documents
            avg_doc_length: Average document length

        Returns:
            BM25 score (higher = more relevant)
        """
        score = 0.0
        doc_length = len(doc_tokens)
        doc_term_counts = Counter(doc_tokens)

        for term in query_tokens:
            if term not in doc_term_counts:
                continue

            # Term frequency in this document
            tf = doc_term_counts[term]

            # Document frequency (number of docs containing term)
            df = doc_frequencies.get(term, 0)

            # Inverse document frequency
            idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)

            # BM25 term score
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / avg_doc_length)

            score += idf * (numerator / denominator)

        return score


# =============================================================================
# INDEXING FUNCTIONS
# =============================================================================

def index_note(note_id: int):
    """Index a single note for RAG retrieval."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get note content
    cursor.execute("""
        SELECT n.id, n.title, n.topic, n.content, n.subject_id, s.name as subject_name
        FROM notes n
        JOIN subjects s ON n.subject_id = s.id
        WHERE n.id = ?
    """, (note_id,))

    note = cursor.fetchone()
    if not note:
        conn.close()
        return

    # Combine title, topic, and content for indexing
    full_text = f"{note['title']}. {note['topic'] or ''}. {note['content']}"
    tokens = tokenize(full_text)
    tokens_json = json.dumps(tokens)

    # Generate embedding if semantic search available
    embedding = None
    if SEMANTIC_AVAILABLE:
        embedding = _generate_embedding(full_text)

    # Upsert chunk
    cursor.execute("""
        INSERT OR REPLACE INTO rag_chunks
        (source_type, source_id, subject_id, title, content, tokens, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('note', note_id, note['subject_id'],
          f"{note['subject_name']}: {note['title']}", full_text, tokens_json, embedding))

    conn.commit()
    conn.close()

    # Update BM25 statistics
    _update_bm25_stats()


def index_flashcard(flashcard_id: int):
    """Index a single flashcard for RAG retrieval."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT f.id, f.question, f.answer, f.topic, f.subject_id, s.name as subject_name
        FROM flashcards f
        JOIN subjects s ON f.subject_id = s.id
        WHERE f.id = ?
    """, (flashcard_id,))

    card = cursor.fetchone()
    if not card:
        conn.close()
        return

    # Combine Q&A for indexing
    full_text = f"Q: {card['question']} A: {card['answer']}"
    if card['topic']:
        full_text = f"[{card['topic']}] {full_text}"

    tokens = tokenize(full_text)
    tokens_json = json.dumps(tokens)

    embedding = None
    if SEMANTIC_AVAILABLE:
        embedding = _generate_embedding(full_text)

    cursor.execute("""
        INSERT OR REPLACE INTO rag_chunks
        (source_type, source_id, subject_id, title, content, tokens, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('flashcard', flashcard_id, card['subject_id'],
          f"{card['subject_name']} Flashcard: {card['topic'] or 'General'}", full_text, tokens_json, embedding))

    conn.commit()
    conn.close()
    _update_bm25_stats()


def index_past_paper_topic(paper_id: int, question_id: int):
    """Index a past paper question topic for RAG retrieval."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pq.id, pq.question_number, pq.topic, pq.notes, pq.max_marks, pq.marks_achieved,
               pp.paper_name, pp.subject_id, s.name as subject_name
        FROM paper_questions pq
        JOIN past_papers pp ON pq.paper_id = pp.id
        JOIN subjects s ON pp.subject_id = s.id
        WHERE pq.id = ?
    """, (question_id,))

    question = cursor.fetchone()
    if not question or not question['topic']:
        conn.close()
        return

    # Create content about this topic performance
    percentage = round(question['marks_achieved'] / question['max_marks'] * 100) if question['max_marks'] > 0 else 0
    full_text = f"Topic: {question['topic']}. Paper: {question['paper_name']}. " \
                f"Score: {question['marks_achieved']}/{question['max_marks']} ({percentage}%). " \
                f"{question['notes'] or ''}"

    tokens = tokenize(full_text)
    tokens_json = json.dumps(tokens)

    embedding = None
    if SEMANTIC_AVAILABLE:
        embedding = _generate_embedding(full_text)

    cursor.execute("""
        INSERT OR REPLACE INTO rag_chunks
        (source_type, source_id, subject_id, title, content, tokens, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('paper_question', question_id, question['subject_id'],
          f"{question['subject_name']}: {question['topic']}", full_text, tokens_json, embedding))

    conn.commit()
    conn.close()
    _update_bm25_stats()


def index_note_image(image_id: int):
    """Index a note image's extracted text for RAG retrieval."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ni.id, ni.note_id, ni.extracted_text, ni.original_filename,
               n.title as note_title, n.subject_id, s.name as subject_name
        FROM note_images ni
        JOIN notes n ON ni.note_id = n.id
        JOIN subjects s ON n.subject_id = s.id
        WHERE ni.id = ?
    """, (image_id,))

    image = cursor.fetchone()
    if not image or not image['extracted_text']:
        conn.close()
        return

    # Index the extracted text from the image
    full_text = f"OCR from image: {image['original_filename']}. {image['extracted_text']}"
    tokens = tokenize(full_text)
    tokens_json = json.dumps(tokens)

    embedding = None
    if SEMANTIC_AVAILABLE:
        embedding = _generate_embedding(full_text)

    cursor.execute("""
        INSERT OR REPLACE INTO rag_chunks
        (source_type, source_id, subject_id, title, content, tokens, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('note_image', image_id, image['subject_id'],
          f"{image['subject_name']}: {image['note_title']} (Image)", full_text, tokens_json, embedding))

    conn.commit()
    conn.close()
    _update_bm25_stats()


def index_all_content():
    """Index all notes, flashcards, past paper topics, and note images."""
    conn = get_connection()
    cursor = conn.cursor()

    # Index all notes
    cursor.execute("SELECT id FROM notes")
    for row in cursor.fetchall():
        index_note(row['id'])

    # Index all flashcards
    cursor.execute("SELECT id FROM flashcards")
    for row in cursor.fetchall():
        index_flashcard(row['id'])

    # Index all past paper questions with topics
    cursor.execute("SELECT id FROM paper_questions WHERE topic IS NOT NULL AND topic != ''")
    for row in cursor.fetchall():
        index_past_paper_topic(None, row['id'])

    # Index all note images (if table exists)
    try:
        cursor.execute("SELECT id FROM note_images WHERE extracted_text IS NOT NULL")
        for row in cursor.fetchall():
            index_note_image(row['id'])
    except sqlite3.OperationalError:
        pass  # note_images table doesn't exist yet

    conn.close()
    _update_bm25_stats()

    return get_index_stats()


def remove_from_index(source_type: str, source_id: int):
    """Remove a document from the index."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rag_chunks WHERE source_type = ? AND source_id = ?",
                   (source_type, source_id))
    conn.commit()
    conn.close()
    _update_bm25_stats()


def _update_bm25_stats():
    """Update BM25 statistics after indexing changes."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get all documents
    cursor.execute("SELECT tokens FROM rag_chunks")
    rows = cursor.fetchall()

    if not rows:
        cursor.execute("""
            UPDATE rag_stats SET total_docs = 0, avg_doc_length = 0, doc_frequencies = '{}'
        """)
        conn.commit()
        conn.close()
        return

    total_docs = len(rows)
    total_length = 0
    doc_frequencies = Counter()

    for row in rows:
        tokens = json.loads(row['tokens'])
        total_length += len(tokens)
        # Count unique terms per document
        unique_terms = set(tokens)
        for term in unique_terms:
            doc_frequencies[term] += 1

    avg_doc_length = total_length / total_docs if total_docs > 0 else 0

    cursor.execute("""
        UPDATE rag_stats
        SET total_docs = ?, avg_doc_length = ?, doc_frequencies = ?, updated_at = ?
        WHERE id = 1
    """, (total_docs, avg_doc_length, json.dumps(doc_frequencies), datetime.now()))

    conn.commit()
    conn.close()


# =============================================================================
# SEMANTIC SEARCH (Optional)
# =============================================================================

_embedding_model = None

def _get_embedding_model():
    """Lazy-load the embedding model."""
    global _embedding_model
    if _embedding_model is None and SEMANTIC_AVAILABLE:
        # Use a small, fast model suitable for study content
        _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedding_model


def _generate_embedding(text: str) -> Optional[bytes]:
    """Generate embedding for text."""
    if not SEMANTIC_AVAILABLE:
        return None

    model = _get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tobytes()


def _cosine_similarity(a: bytes, b: bytes) -> float:
    """Calculate cosine similarity between two embeddings."""
    if not SEMANTIC_AVAILABLE:
        return 0.0

    vec_a = np.frombuffer(a, dtype=np.float32)
    vec_b = np.frombuffer(b, dtype=np.float32)

    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


# =============================================================================
# RETRIEVAL FUNCTIONS
# =============================================================================

def search(query: str, top_k: int = 5, subject_id: int = None,
           source_types: List[str] = None, use_semantic: bool = True) -> List[Dict]:
    """
    Search indexed content using BM25 (and optionally semantic search).

    Args:
        query: Search query
        top_k: Number of results to return
        subject_id: Optional filter by subject
        source_types: Optional filter by source type ('note', 'flashcard', 'paper_question')
        use_semantic: Whether to use semantic search if available

    Returns:
        List of results with score, title, content, and metadata
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get BM25 stats
    cursor.execute("SELECT total_docs, avg_doc_length, doc_frequencies FROM rag_stats WHERE id = 1")
    stats_row = cursor.fetchone()

    if not stats_row or stats_row['total_docs'] == 0:
        conn.close()
        return []

    total_docs = stats_row['total_docs']
    avg_doc_length = stats_row['avg_doc_length']
    doc_frequencies = json.loads(stats_row['doc_frequencies'])

    # Build query for chunks
    sql = "SELECT * FROM rag_chunks WHERE 1=1"
    params = []

    if subject_id:
        sql += " AND subject_id = ?"
        params.append(subject_id)

    if source_types:
        placeholders = ','.join('?' * len(source_types))
        sql += f" AND source_type IN ({placeholders})"
        params.extend(source_types)

    cursor.execute(sql, params)
    chunks = cursor.fetchall()
    conn.close()

    if not chunks:
        return []

    # Tokenize query
    query_tokens = tokenize(query)

    # Score documents
    bm25 = BM25()
    results = []

    # Generate query embedding for semantic search
    query_embedding = None
    if use_semantic and SEMANTIC_AVAILABLE:
        query_embedding = _generate_embedding(query)

    # Check if query has any keyword matches (helps decide scoring weight)
    query_has_keyword_matches = any(
        term in doc_frequencies for term in query_tokens
    )

    for chunk in chunks:
        doc_tokens = json.loads(chunk['tokens'])

        # BM25 score
        bm25_score = bm25.score(query_tokens, doc_tokens, doc_frequencies, total_docs, avg_doc_length)

        # Semantic score (if available)
        semantic_score = 0.0
        if query_embedding and chunk['embedding']:
            semantic_score = _cosine_similarity(query_embedding, chunk['embedding'])

        # Improved combined scoring:
        # - If BM25 finds matches, use balanced weighting
        # - If BM25 finds nothing but semantic finds something, rely on semantic
        # - This allows "how plants make energy" to find "photosynthesis"
        if bm25_score > 0 and semantic_score > 0:
            # Both methods found something - balanced weighting
            combined_score = 0.4 * bm25_score + 0.6 * (semantic_score * 10)
        elif bm25_score > 0:
            # Only keyword match
            combined_score = bm25_score
        elif semantic_score > 0.3:  # Semantic threshold for relevance
            # Only semantic match - this enables conceptual queries
            # "how plants make energy" -> "photosynthesis"
            combined_score = semantic_score * 10
        else:
            combined_score = 0

        # Include results above threshold
        if combined_score > 0.1:
            results.append({
                'id': chunk['id'],
                'source_type': chunk['source_type'],
                'source_id': chunk['source_id'],
                'subject_id': chunk['subject_id'],
                'title': chunk['title'],
                'content': chunk['content'],
                'score': combined_score,
                'bm25_score': bm25_score,
                'semantic_score': semantic_score
            })

    # Sort by score and return top_k
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]


def get_context_for_query(query: str, max_tokens: int = 2000,
                          subject_id: int = None) -> Tuple[str, List[Dict]]:
    """
    Get formatted context for a query to send to Claude.

    Args:
        query: User's question
        max_tokens: Maximum approximate tokens for context
        subject_id: Optional subject filter

    Returns:
        Tuple of (formatted_context_string, list_of_sources)
    """
    # Search for relevant content
    results = search(query, top_k=10, subject_id=subject_id)

    if not results:
        return "", []

    # Build context string, respecting token limit
    # Rough estimate: 1 token ~= 4 characters
    max_chars = max_tokens * 4

    context_parts = []
    sources = []
    current_chars = 0

    for result in results:
        # Format this result
        source_label = {
            'note': 'Note',
            'flashcard': 'Flashcard',
            'paper_question': 'Past Paper Topic'
        }.get(result['source_type'], 'Document')

        entry = f"[{source_label}] {result['title']}\n{result['content']}\n"

        if current_chars + len(entry) > max_chars:
            break

        context_parts.append(entry)
        sources.append({
            'type': result['source_type'],
            'title': result['title'],
            'score': result['score']
        })
        current_chars += len(entry)

    if not context_parts:
        return "", []

    context = "Here is relevant information from your study materials:\n\n"
    context += "---\n".join(context_parts)
    context += "\n---\n\nUse this information to help answer the question."

    return context, sources


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_index_stats() -> Dict:
    """Get statistics about the RAG index."""
    conn = get_connection()
    cursor = conn.cursor()

    # Count by source type
    cursor.execute("""
        SELECT source_type, COUNT(*) as count
        FROM rag_chunks
        GROUP BY source_type
    """)
    type_counts = {row['source_type']: row['count'] for row in cursor.fetchall()}

    # Get BM25 stats
    cursor.execute("SELECT total_docs, avg_doc_length FROM rag_stats WHERE id = 1")
    stats = cursor.fetchone()

    conn.close()

    # Count documents with embeddings
    cursor = get_connection().cursor()
    cursor.execute("SELECT COUNT(*) as count FROM rag_chunks WHERE embedding IS NOT NULL")
    docs_with_embeddings = cursor.fetchone()['count']
    cursor.connection.close()

    return {
        'total_documents': stats['total_docs'] if stats else 0,
        'avg_document_length': round(stats['avg_doc_length'], 1) if stats else 0,
        'notes_indexed': type_counts.get('note', 0),
        'flashcards_indexed': type_counts.get('flashcard', 0),
        'paper_topics_indexed': type_counts.get('paper_question', 0),
        'note_images_indexed': type_counts.get('note_image', 0),
        'semantic_search_available': SEMANTIC_AVAILABLE,
        'semantic_status': get_semantic_status(),
        'documents_with_embeddings': docs_with_embeddings
    }


def clear_index():
    """Clear all indexed content."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rag_chunks")
    cursor.execute("UPDATE rag_stats SET total_docs = 0, avg_doc_length = 0, doc_frequencies = '{}'")
    conn.commit()
    conn.close()


# Initialize RAG database tables
init_rag_database()
