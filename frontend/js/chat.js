javascript
// ============================================================
// AIOCEAN - CONFIGURACIÓN DE API
// ============================================================

// URL de tu API en Render o localhost para pruebas locales.
const API_BASE_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://localhost:8000"
        : "https://aiocean-cloud-core.onrender.com";


// ============================================================
// INICIALIZACIÓN
// ============================================================

document.addEventListener("DOMContentLoaded", () => {
    const chatInput = document.getElementById("chat-input-field");
    const btnSend = document.getElementById("btn-send");
    const messagesContainer = document.getElementById("chat-messages");


    // ========================================================
    // ENVIAR MENSAJE
    // ========================================================

    async function sendMessage() {
        const text = chatInput.value.trim();

        if (!text) {
            return;
        }

        // Mostrar mensaje del usuario
        appendUserMessage(text);

        // Limpiar input
        chatInput.value = "";

        // Crear bloque vacío para la respuesta de AIOCEAN
        const aiMessageBody = createAIMessageBlock();

        try {
            const response = await fetch(
                `${API_BASE_URL}/api/chat/stream`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        user_id: "default_user",
                        message: text,
                        stream: true
                    })
                }
            );


            // ====================================================
            // COMPROBAR RESPUESTA DEL SERVIDOR
            // ====================================================

            if (!response.ok) {
                aiMessageBody.textContent =
                    "❌ Error al conectar con el servidor Backend.";

                return;
            }


            // Comprobar que el navegador recibió un stream
            if (!response.body) {
                aiMessageBody.textContent =
                    "❌ El servidor no devolvió un flujo de datos.";

                return;
            }


            // ====================================================
            // LECTURA DEL STREAM SSE
            // ====================================================

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    break;
                }


                // Decodificar los datos recibidos
                buffer += decoder.decode(value, {
                    stream: true
                });


                // Separar eventos SSE
                const events = buffer.split("\n\n");

                // Guardar el último evento incompleto
                buffer = events.pop() || "";


                // Procesar eventos completos
                for (const event of events) {
                    const lines = event.split("\n");

                    for (const line of lines) {

                        // Solo procesamos líneas data:
                        if (!line.startsWith("data:")) {
                            continue;
                        }


                        // Obtener contenido después de "data:"
                        const dataStr = line
                            .substring(5)
                            .trim();


                        // Final del stream
                        if (dataStr === "[DONE]") {
                            return;
                        }


                        // Intentar interpretar JSON
                        try {
                            const parsed = JSON.parse(dataStr);

                            if (parsed.content) {
                                aiMessageBody.textContent += parsed.content;

                                // Mantener visible el último mensaje
                                messagesContainer.scrollTop =
                                    messagesContainer.scrollHeight;
                            }

                        } catch (error) {
                            console.error(
                                "Error parseando evento SSE:",
                                error,
                                dataStr
                            );
                        }
                    }
                }
            }

        } catch (error) {

            console.error(
                "Error conectando con AIOCEAN:",
                error
            );

            aiMessageBody.textContent =
                "⚠️ Error de red o servidor no disponible.";
        }
    }


    // ========================================================
    // MENSAJE DEL USUARIO
    // ========================================================

    function appendUserMessage(text) {
        const msgBlock = document.createElement("div");

        msgBlock.className = "msg-user-block";

        msgBlock.innerHTML = `
            <div class="msg-user-label">
                USER:
            </div>

            <div class="msg-user-body">
                ${escapeHTML(text)}
            </div>
        `;

        messagesContainer.appendChild(msgBlock);

        // Scroll automático
        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;
    }


    // ========================================================
    // BLOQUE DE RESPUESTA DE AIOCEAN
    // ========================================================

    function createAIMessageBlock() {
        const msgBlock = document.createElement("div");

        msgBlock.className = "msg-ai-block";

        msgBlock.innerHTML = `
            <div class="msg-ai-header">
                AIOCEAN
            </div>

            <div class="msg-ai-label">
                AIOCEAN [LOCAL QWEN]:
            </div>

            <div class="msg-ai-body"></div>
        `;

        messagesContainer.appendChild(msgBlock);

        // Scroll automático
        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;

        return msgBlock.querySelector(".msg-ai-body");
    }


    // ========================================================
    // PROTECCIÓN CONTRA HTML
    // ========================================================

    function escapeHTML(str) {
        const map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return str.replace(
            /[&<>"']/g,
            (tag) => map[tag]
        );
    }


    // ========================================================
    // EVENTO DEL BOTÓN ENVIAR
    // ========================================================

    if (btnSend) {
        btnSend.addEventListener(
            "click",
            sendMessage
        );
    }


    // ========================================================
    // EVENTO ENTER
    // ========================================================

    if (chatInput) {
        chatInput.addEventListener(
            "keydown",
            (event) => {

                if (event.key === "Enter") {

                    // Evitar salto de línea
                    event.preventDefault();

                    sendMessage();
                }
            }
        );
    }
});