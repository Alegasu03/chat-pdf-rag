# Chat PDF RAG 📚🤖

Un proyecto de **Retrieval-Augmented Generation (RAG)** que permite interactuar con documentos PDF mediante conversación natural. Lee, consulta y extrae información de tus PDFs usando inteligencia artificial.

## 🌟 Características

- 📄 **Lectura de PDFs**: Carga y procesa múltiples documentos PDF
- 💬 **Chat Inteligente**: Realiza preguntas sobre el contenido de tus documentos
- 🧠 **RAG (Retrieval-Augmented Generation)**: Búsqueda semántica y generación contextual de respuestas
- 🚀 **Interfaz Moderna**: Frontend intuitivo y responsive
- 🔄 **Backend Robusto**: API REST para procesamiento de documentos y consultas
- 📊 **Búsqueda Inteligente**: Encuentra información relevante en tus documentos rápidamente

## 🛠️ Stack Tecnológico

### Frontend
- **JavaScript** (21.7%)
- **HTML** (6.3%)
- **CSS** (17.5%)

### Backend
- **Python** (54.5%)

## 📋 Requisitos Previos

- Python 3.8+
- Node.js 14+
- npm o yarn

## 🚀 Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

La aplicación estará disponible en `http://localhost:3000`

## 📖 Uso

1. **Carga un PDF**: Selecciona un documento PDF desde la interfaz
2. **Procesa el contenido**: El sistema extraerá y indexará el contenido
3. **Realiza preguntas**: Escribe tus consultas en el chat
4. **Obtén respuestas**: Recibe respuestas contextualmente relevantes basadas en el documento

## 🏗️ Estructura del Proyecto

```
chat-pdf-rag/
├── backend/          # API y lógica RAG (Python)
├── frontend/         # Interfaz de usuario (JavaScript/React)
└── README.md        # Este archivo
```

## 🔧 Configuración

Asegúrate de configurar las siguientes variables de entorno en el backend:

```bash
FLASK_ENV=development
PDF_UPLOAD_PATH=./uploads
```

## 📄 Licencia

Este proyecto está bajo licencia abierta. Ver `LICENSE` para más detalles.

## 👤 Autor

**Alegasu03** - [GitHub Profile](https://github.com/Alegasu03)

## 📞 Soporte

Si encuentras problemas o tienes sugerencias, abre un issue en el repositorio.

---

⭐ Si te ha sido útil, ¡no olvides dejar una estrella!
