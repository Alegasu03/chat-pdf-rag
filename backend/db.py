import sqlite3
import json
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rag.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


def ensure_column_exists(table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    doc_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    chunks TEXT NOT NULL,
    embeddings TEXT NOT NULL,
    doc_embedding TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    conversation_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL
)
""")

ensure_column_exists("conversations", "user_id", "TEXT")
ensure_column_exists("documents", "user_id", "TEXT")

conn.commit()


def to_json_array(value):
    if isinstance(value, np.ndarray):
        return json.dumps(value.tolist())
    return json.dumps(value)


def create_user(user_id, email, password_hash):
    cursor.execute("""
        INSERT INTO users (user_id, email, password_hash)
        VALUES (?, ?, ?)
    """, (user_id, email, password_hash))

    conn.commit()


def get_user_by_email(email):
    cursor.execute("""
        SELECT user_id, email, password_hash
        FROM users
        WHERE email = ?
    """, (email,))

    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "email": row[1],
        "password_hash": row[2]
    }


def get_user_by_id(user_id):
    cursor.execute("""
        SELECT user_id, email
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "email": row[1]
    }


def save_document(doc_id, user_id, filename, chunks, embeddings, doc_embedding):
    cursor.execute("""
        INSERT OR REPLACE INTO documents
        (doc_id, user_id, filename, chunks, embeddings, doc_embedding)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        doc_id,
        user_id,
        filename,
        json.dumps(chunks),
        to_json_array(embeddings),
        to_json_array(doc_embedding)
    ))

    conn.commit()


def load_documents(user_id=None):
    if user_id:
        cursor.execute("""
            SELECT doc_id, user_id, filename, chunks, embeddings, doc_embedding
            FROM documents
            WHERE user_id = ?
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT doc_id, user_id, filename, chunks, embeddings, doc_embedding
            FROM documents
        """)

    rows = cursor.fetchall()
    docs = {}

    for row in rows:
        doc_id, user_id, filename, chunks, embeddings, doc_embedding = row

        docs[doc_id] = {
            "doc_id": doc_id,
            "user_id": user_id,
            "filename": filename,
            "chunks": json.loads(chunks),
            "embeddings": np.array(json.loads(embeddings)),
            "doc_embedding": np.array(json.loads(doc_embedding))
        }

    return docs


def get_documents(user_id=None):
    if user_id:
        cursor.execute("""
            SELECT doc_id, filename
            FROM documents
            WHERE user_id = ?
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT doc_id, filename
            FROM documents
        """)

    rows = cursor.fetchall()

    return [
        {
            "doc_id": row[0],
            "filename": row[1]
        }
        for row in rows
    ]


def get_documents_by_user(user_id):
    return get_documents(user_id=user_id)


def get_document(doc_id, user_id=None):
    if user_id:
        cursor.execute("""
            SELECT doc_id, user_id, filename, chunks, embeddings, doc_embedding
            FROM documents
            WHERE doc_id = ? AND user_id = ?
        """, (doc_id, user_id))
    else:
        cursor.execute("""
            SELECT doc_id, user_id, filename, chunks, embeddings, doc_embedding
            FROM documents
            WHERE doc_id = ?
        """, (doc_id,))

    row = cursor.fetchone()

    if row is None:
        return None

    chunks = json.loads(row[3])

    return {
        "doc_id": row[0],
        "user_id": row[1],
        "filename": row[2],
        "chunks": chunks,
        "embeddings": np.array(json.loads(row[4])),
        "doc_embedding": np.array(json.loads(row[5])),
        "num_chunks": len(chunks)
    }


def get_document_by_user(doc_id, user_id):
    document = get_document(doc_id=doc_id, user_id=user_id)

    if document is None:
        return None

    return {
        "doc_id": document["doc_id"],
        "user_id": document["user_id"],
        "filename": document["filename"],
        "num_chunks": document["num_chunks"]
    }


def delete_document(doc_id, user_id=None):
    if user_id:
        cursor.execute("""
            DELETE FROM documents
            WHERE doc_id = ? AND user_id = ?
        """, (doc_id, user_id))
    else:
        cursor.execute("""
            DELETE FROM documents
            WHERE doc_id = ?
        """, (doc_id,))

    conn.commit()
    return cursor.rowcount > 0


def delete_document_by_user(doc_id, user_id):
    return delete_document(doc_id=doc_id, user_id=user_id)


def save_message(user_id, conversation_id, question, answer):
    cursor.execute("""
        INSERT INTO conversations
        (user_id, conversation_id, question, answer)
        VALUES (?, ?, ?, ?)
    """, (user_id, conversation_id, question, answer))

    conn.commit()


def load_conversation(conversation_id, user_id=None, limit=5):
    if user_id:
        cursor.execute("""
            SELECT question, answer
            FROM conversations
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (conversation_id, user_id, limit))
    else:
        cursor.execute("""
            SELECT question, answer
            FROM conversations
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (conversation_id, limit))

    rows = cursor.fetchall()

    return [
        {
            "question": row[0],
            "answer": row[1]
        }
        for row in reversed(rows)
    ]


def close_connection():
    conn.close()