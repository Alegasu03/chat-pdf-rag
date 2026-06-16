const API = "http://127.0.0.1:8000";

let conversationId = localStorage.getItem("conversation_id");

// ---------------- AUTH HELPERS ----------------

function getToken() {
    return localStorage.getItem("token");
}

function getAuthHeaders() {
    return {
        Authorization: `Bearer ${getToken()}`
    };
}

function isLoggedIn() {
    return !!getToken();
}

function setAuthMessage(message) {
    document.getElementById("authMessage").innerText = message;
}

function updateUI() {
    const token = getToken();
    const email = localStorage.getItem("email");

    const authBox = document.getElementById("authBox");
    const userBox = document.getElementById("userBox");
    const documentsArea = document.getElementById("documentsArea");
    const status = document.getElementById("status");
    const userEmail = document.getElementById("userEmail");

    if (token) {
        authBox.style.display = "none";
        userBox.style.display = "block";
        documentsArea.style.display = "block";
        status.innerText = "● Ready";
        userEmail.innerText = email || "Logged in";

        loadDocs();
    } else {
        authBox.style.display = "block";
        userBox.style.display = "none";
        documentsArea.style.display = "none";
        status.innerText = "● Not logged in";
        userEmail.innerText = "";
    }
}

// ---------------- REGISTER ----------------

async function register() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        setAuthMessage("Introduce email y contraseña");
        return;
    }

    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        setAuthMessage(data.detail || "Error al registrarse");
        return;
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("email", data.email);
    localStorage.removeItem("conversation_id");
    conversationId = null;

    setAuthMessage("");
    updateUI();
}

// ---------------- LOGIN ----------------

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
        setAuthMessage("Introduce email y contraseña");
        return;
    }

    const res = await fetch(`${API}/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (!res.ok) {
        setAuthMessage(data.detail || "Error al iniciar sesión");
        return;
    }

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("email", data.email);
    localStorage.removeItem("conversation_id");
    conversationId = null;

    setAuthMessage("");
    updateUI();
}

// ---------------- LOGOUT ----------------

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    localStorage.removeItem("conversation_id");

    conversationId = null;

    document.getElementById("docsList").innerHTML = "";
    document.getElementById("chatBox").innerHTML = "";

    updateUI();
}

// ---------------- CHAT ----------------

async function ask() {
    if (!isLoggedIn()) {
        alert("Inicia sesión primero");
        return;
    }

    const input = document.getElementById("question");
    const question = input.value.trim();

    if (!question) return;

    addMessage(question, "user");
    input.value = "";

    const res = await fetch(`${API}/ask/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders()
        },
        body: JSON.stringify({
            question,
            conversation_id: conversationId
        })
    });

    const data = await res.json();

    if (!res.ok) {
        addMessage(data.detail || "Error al preguntar", "bot");
        return;
    }

    conversationId = data.conversation_id;
    localStorage.setItem("conversation_id", conversationId);

    addMessage(data.answer, "bot");
}

function addMessage(text, type) {
    const chat = document.getElementById("chatBox");

    const div = document.createElement("div");
    div.className = type === "user" ? "msg-user" : "msg-bot";
    div.innerText = text;

    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

// ---------------- UPLOAD ----------------

async function uploadPDF() {
    if (!isLoggedIn()) {
        alert("Inicia sesión primero");
        return;
    }

    const file = document.getElementById("fileInput").files[0];

    if (!file) {
        alert("Selecciona un PDF primero");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API}/upload/`, {
        method: "POST",
        headers: {
            ...getAuthHeaders()
        },
        body: formData
    });

    const data = await res.json();

    if (!res.ok) {
        alert(data.detail || "Error al subir PDF");
        return;
    }

    document.getElementById("fileInput").value = "";
    document.getElementById("selectedFileName").innerText = "No file selected";
    
    loadDocs();
}

// ---------------- LOAD DOCS ----------------

async function loadDocs() {
    if (!isLoggedIn()) return;

    const res = await fetch(`${API}/documents`, {
        headers: {
            ...getAuthHeaders()
        }
    });

    const docs = await res.json();

    if (!res.ok) {
        if (res.status === 401 || res.status === 403) {
            logout();
        }
        return;
    }

    const container = document.getElementById("docsList");
    container.innerHTML = "";

    docs.forEach(doc => {
        const div = document.createElement("div");
        div.className = "doc";

        div.innerHTML = `
            <span>${doc.filename}</span>
            <button class="delete" onclick="deleteDoc('${doc.doc_id}')">×</button>
        `;

        container.appendChild(div);
    });
}

// ---------------- DELETE DOC ----------------

async function deleteDoc(docId) {
    if (!isLoggedIn()) {
        alert("Inicia sesión primero");
        return;
    }

    const confirmed = confirm("¿Seguro que quieres eliminar este documento? Esta acción no se puede deshacer.");

    if (!confirmed) return;

    const res = await fetch(`${API}/documents/${docId}`, {
        method: "DELETE",
        headers: {
            ...getAuthHeaders()
        }
    });

    if (!res.ok) {
        const data = await res.json();
        alert(data.detail || "Error al eliminar documento");
        return;
    }

    loadDocs();
}

const fileInput = document.getElementById("fileInput");

if (fileInput) {
    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];

        document.getElementById("selectedFileName").innerText =
            file ? file.name : "No file selected";
    });
}

document.addEventListener("DOMContentLoaded", updateUI);