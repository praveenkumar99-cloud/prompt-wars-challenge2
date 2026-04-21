const sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const suggestionsContainer = document.getElementById('suggestions-container');
const sourcesContainer = document.getElementById('sources-container');
const sourcesList = document.getElementById('sources-list');

function appendMessage(content, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    // Format links and bold text
    const formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    contentDiv.innerHTML = formattedContent;
    
    div.appendChild(contentDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'message assistant';
    div.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'typing-indicator';
    contentDiv.innerHTML = '<span></span><span></span><span></span>';
    
    div.appendChild(contentDiv);
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function updateSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';
    suggestions.forEach(suggestion => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-btn';
        btn.textContent = suggestion;
        btn.onclick = () => useSuggestion(suggestion);
        suggestionsContainer.appendChild(btn);
    });
}

function updateSources(sources) {
    if (sources && sources.length > 0) {
        sourcesContainer.style.display = 'block';
        sourcesList.innerHTML = '';
        sources.forEach(source => {
            const li = document.createElement('li');
            li.textContent = source;
            sourcesList.appendChild(li);
        });
    } else {
        sourcesContainer.style.display = 'none';
        sourcesList.innerHTML = '';
    }
}

function useSuggestion(text) {
    userInput.value = text;
    sendMessage();
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // UI Updates
    appendMessage(message, 'user');
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
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
        appendMessage(data.response, 'assistant');
        updateSuggestions(data.follow_up_suggestions || []);
        updateSources(data.sources || []);
        
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        appendMessage("I'm sorry, I'm having trouble connecting right now. Please try again.", 'assistant');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}
