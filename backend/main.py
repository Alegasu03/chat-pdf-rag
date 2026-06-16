from fastapi import Depends, FastAPI, UploadFile, File, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import shutil
import os
import uuid
from uuid import uuid4
from typing import Optional
import glob
from pydantic import BaseModel, EmailStr, Field
from dotenv import load_dotenv
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

from backend.pdf_utils import extract_text, chunk_text

from backend.db import (
    create_user,
    get_user_by_email,
    get_document_by_user,
    get_documents_by_user,
    save_document,
    load_documents,
    load_conversation,
    save_message,
    delete_document_by_user
)

from backend.services.embedding_service import EmbeddingService
from backend.services.llm_service import LLMService
from backend.services.rag_service import RAGService


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


embedding_service = EmbeddingService()

llm_service = LLMService(
    api_key=os.getenv("LLM_API_KEY")
)

pdf_store = {}


@app.get("/")
def read_root():
    return {"message": "API funcionando"}


@app.post("/register")
def register(data: RegisterRequest):
    existing_user = get_user_by_email(data.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe"
        )

    user_id = str(uuid4())
    password_hash = hash_password(data.password)

    create_user(
        user_id=user_id,
        email=data.email,
        password_hash=password_hash
    )

    token = create_access_token({"sub": user_id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "email": data.email
    }


@app.post("/login")
def login(data: LoginRequest):
    user = get_user_by_email(data.email)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )

    if not verify_password(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )

    token = create_access_token({"sub": user["user_id"]})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["user_id"],
        "email": user["email"]
    }


@app.post("/upload/")
def upload_pdf(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    doc_id = str(uuid.uuid4())

    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(file_path)
    chunks = chunk_text(text)

    embeddings = embedding_service.embed_chunks(chunks)
    doc_embedding = embedding_service.embed_text(text)

    
    save_document(
        doc_id=doc_id,
        user_id=user_id,
        filename=file.filename,
        chunks=chunks,
        embeddings=embeddings,
        doc_embedding=doc_embedding
    )

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "message": "Archivo procesado correctamente"
    }


@app.post("/ask/")
def ask_question(
    question: str = Body(...),
    conversation_id: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    if not conversation_id:
        conversation_id = str(uuid4())

    user_pdf_store = load_documents(user_id=user_id)

    if not user_pdf_store:
        raise HTTPException(
            status_code=404,
            detail="No tienes documentos subidos"
        )

    user_rag_service = RAGService(user_pdf_store, embedding_service)

    query_embedding = embedding_service.embed_text(question)

    best_doc_id = user_rag_service.select_best_doc(query_embedding)

    if best_doc_id is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró ningún documento relevante"
        )

    used_chunks = user_rag_service.retrieve_chunks(
        best_doc_id,
        query_embedding,
        top_k=3
    )

    context = "\n\n".join(used_chunks)

    history = load_conversation(
        conversation_id=conversation_id,
        user_id=user_id
    )

    history_text = ""
    for msg in history[-5:]:
        history_text += f"""
Usuario: {msg["question"]}
Asistente: {msg["answer"]}
"""

    prompt = f"""
Eres un asistente que responde únicamente utilizando el contexto proporcionado.

Si la respuesta no aparece en el contexto, indica claramente:
"No encuentro esa información en los documentos proporcionados."

Historial:
{history_text}

Contexto:
{context}

Pregunta:
{question}
"""

    answer = llm_service.generate(prompt)

    save_message(
        user_id=user_id,
        conversation_id=conversation_id,
        question=question,
        answer=answer
    )

    return {
        "answer": answer,
        "conversation_id": conversation_id,
        "source_doc_id": best_doc_id,
        "used_chunks": used_chunks
    }


@app.get("/documents")
def list_documents(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    return get_documents_by_user(user_id)


@app.get("/documents/{doc_id}")
def document_details(
    doc_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    document = get_document_by_user(doc_id, user_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    return document


@app.delete("/documents/{doc_id}")
def remove_document(
    doc_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["user_id"]

    deleted = delete_document_by_user(doc_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado"
        )

    # borrar archivo físico
    matching_files = glob.glob(
        os.path.join(UPLOAD_DIR, f"{doc_id}_*")
    )

    for file_path in matching_files:
        try:
            os.remove(file_path)
        except OSError:
            pass

    return {
        "message": "Documento eliminado"
    }