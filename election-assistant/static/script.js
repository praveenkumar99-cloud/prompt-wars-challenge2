const sessionId = "sess_" + Math.random().toString(36).slice(2, 11);
const chatMessages = document.getElementById("chat-messages");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const suggestionsContainer = document.getElementById("suggestions-container");
const sourcesContainer = document.getElementById("sources-container");
const sourcesList = document.getElementById("sources-list");
const serviceBadge = document.getElementById("service-badge");

function appendFormattedText(container, content) {
    const lines = content.split("\n");

    lines.forEach((line, lineIndex) => {
        const segments = line.split(/(\*\*.*?\*\*)/g);

        segments.forEach((segment) => {
            if (!segment) return;

            if (segment.startsWith("**") && segment.endsWith("**") && segment.length > 4) {
                const strong = document.createElement("strong");
                strong.textContent = segment.slice(2, -2);
                container.appendChild(strong);
                return;
            }

            container.appendChild(document.createTextNode(segment));
        });

        if (lineIndex < lines.length - 1) {
            container.appendChild(document.createElement("br"));
        }
    });
}

function appendMessage(content, role) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    appendFormattedText(contentDiv, content);

    div.appendChild(contentDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const div = document.createElement("div");
    div.className = "message assistant";
    div.id = "typing-indicator";

    const contentDiv = document.createElement("div");
    contentDiv.className = "typing-indicator";
    contentDiv.innerHTML = "<span></span><span></span><span></span>";

    div.appendChild(contentDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) {
        indicator.remove();
    }
}

function updateSuggestions(suggestions) {
    suggestionsContainer.innerHTML = "";
    suggestions.forEach((suggestion) => {
        const btn = document.createElement("button");
        btn.className = "suggestion-btn";
        btn.textContent = suggestion;
        btn.type = "button";
        btn.onclick = () => useSuggestion(suggestion);
        suggestionsContainer.appendChild(btn);
    });
}

function updateSources(sources) {
    if (sources && sources.length > 0) {
        sourcesContainer.hidden = false;
        sourcesList.innerHTML = "";
        sources.forEach((source) => {
            const li = document.createElement("li");
            li.textContent = source;
            sourcesList.appendChild(li);
        });
    } else {
        sourcesContainer.hidden = true;
        sourcesList.innerHTML = "";
    }
}

function useSuggestion(text) {
    userInput.value = text;
    sendMessage();
}

async function loadSystemStatus() {
    try {
        const response = await fetch("/api/system/status");
        if (!response.ok) {
            throw new Error(`Status request failed: ${response.status}`);
        }

        const status = await response.json();
        const integrations = [];

        if (status.google_api_key_configured) integrations.push("Gemini");
        if (status.cloud_run_service_url_configured) integrations.push("Cloud Run");

        serviceBadge.textContent = integrations.length > 0
            ? `Connected: ${integrations.join(", ")}`
            : "Local fallback mode";
    } catch (error) {
        console.error("Status error:", error);
        serviceBadge.textContent = "Status unavailable";
    }
}

async function sendMessage(event) {
    if (event) {
        event.preventDefault();
    }

    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    userInput.value = "";
    userInput.disabled = true;
    sendBtn.disabled = true;
    showTypingIndicator();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        removeTypingIndicator();
        appendMessage(data.response, "assistant");
        updateSuggestions(data.follow_up_suggestions || []);
        updateSources(data.sources || []);
    } catch (error) {
        console.error("Chat error:", error);
        removeTypingIndicator();
        appendMessage("I'm sorry, I'm having trouble connecting right now. Please try again.", "assistant");
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

loadSystemStatus();
