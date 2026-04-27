/**
 * Election Assistant Frontend Script
 * Enhanced with accessibility, voice input, multi-language support, and PDF export
 */

const CONFIG = {
    API_BASE_URL: '/api',
    CHAT_ENDPOINT: '/chat',
    STATUS_ENDPOINT: '/status',
    MAX_MESSAGE_LENGTH: 500,
    SESSION_ID_KEY: 'election-assistant-session-id',
    LANGUAGE_KEY: 'election-assistant-language',
};

let sessionId = localStorage.getItem(CONFIG.SESSION_ID_KEY) || generateSessionId();
let currentLanguage = localStorage.getItem(CONFIG.LANGUAGE_KEY) || 'en';
let isListening = false;
let recognitionSupported = false;
let topicsSet = new Set();

localStorage.setItem(CONFIG.SESSION_ID_KEY, sessionId);

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    console.log('Initializing Election Assistant...');
    checkServiceStatus();
    setupEventListeners();
    setupLanguageSelector();
    checkVoiceSupport();
    announceToScreenReader('Election Assistant page loaded');
}

function checkVoiceSupport() {
    // Check browser support for Web Speech API and initialize voice input.
    const voiceBtn = document.getElementById('voice-input-btn');
    const chatInput = document.getElementById('user-input');

    if (!voiceBtn) return;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        recognition.continuous = false;

        voiceBtn.addEventListener('click', () => {
            voiceBtn.setAttribute('aria-pressed', 'true');
            voiceBtn.setAttribute('aria-label', 'Listening... click to stop');
            voiceBtn.classList.add('listening');
            recognition.start();
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            chatInput.focus();
            voiceBtn.setAttribute('aria-pressed', 'false');
            voiceBtn.setAttribute('aria-label', 'Use voice input to ask a question');
            voiceBtn.classList.remove('listening');
            // Announce to screen readers
            const announcement = document.createElement('div');
            announcement.setAttribute('role', 'status');
            announcement.setAttribute('aria-live', 'polite');
            announcement.className = 'sr-only';
            announcement.textContent = 'Voice input captured: ' + transcript;
            document.body.appendChild(announcement);
            setTimeout(() => document.body.removeChild(announcement), 3000);
        };

        recognition.onerror = (event) => {
            console.warn('Voice recognition error:', event.error);
            voiceBtn.setAttribute('aria-pressed', 'false');
            voiceBtn.setAttribute('aria-label', 'Use voice input to ask a question');
            voiceBtn.classList.remove('listening');
            chatInput.placeholder = 'Voice input unavailable. Type your question here...';
            setTimeout(() => {
                chatInput.placeholder = 'Type your election question here...';
            }, 3000);
        };

        recognition.onend = () => {
            voiceBtn.setAttribute('aria-pressed', 'false');
            voiceBtn.setAttribute('aria-label', 'Use voice input to ask a question');
            voiceBtn.classList.remove('listening');
        };

    } else {
        // Browser does not support voice input — hide gracefully
        voiceBtn.style.display = 'none';
        voiceBtn.setAttribute('aria-hidden', 'true');
    }
}

function setupEventListeners() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleFormSubmit);
    }

    const userInput = document.getElementById('user-input');
    const charCounter = document.getElementById('char-counter');

    if (userInput && charCounter) {
        userInput.addEventListener('input', () => {
            const remaining = 500 - userInput.value.length;
            charCounter.textContent = remaining;
            charCounter.className = 'char-counter';
            if (remaining < 100) charCounter.classList.add('warning');
            if (remaining < 20) {
                charCounter.classList.remove('warning');
                charCounter.classList.add('danger');
            }
        });
    }

    const printBtn = document.getElementById('print-btn');
    if (printBtn) {
        printBtn.addEventListener('click', printConversation);
    }

    const exportBtn = document.getElementById('export-pdf-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportPDF);
    }

    const langSelect = document.getElementById('language-select');
    if (langSelect) {
        langSelect.addEventListener('change', handleLanguageChange);
        langSelect.value = currentLanguage;
    }

    const suggestionContainer = document.getElementById('suggestions-container');
    if (suggestionContainer) {
        const buttons = suggestionContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('keydown', handleSuggestionKeydown);
        });
    }
}

function setupLanguageSelector() {
    const langSelect = document.getElementById('language-select');
    if (langSelect) {
        langSelect.value = currentLanguage;
    }
}

function handleLanguageChange(event) {
    currentLanguage = event.target.value;
    localStorage.setItem(CONFIG.LANGUAGE_KEY, currentLanguage);
    announceToScreenReader(`Language changed to ${currentLanguage === 'en' ? 'English' : 'Spanish'}`);
}

function generateSessionId() {
    return 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

function updateServiceBadge(connected, serviceName) {
    const badge = document.getElementById('service-badge');
    if (!badge) return;
    const statusText = badge.querySelector('.status-text');
    if (connected) {
        badge.classList.add('connected');
        if (statusText) statusText.textContent = 'Connected: ' + (serviceName || 'Gemini');
    } else {
        badge.classList.remove('connected');
        if (statusText) statusText.textContent = 'Connecting...';
    }
}

async function checkServiceStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.STATUS_ENDPOINT}`);
        const data = await response.json();

        if (response.ok) {
            updateServiceBadge(true, 'Gemini');
            announceToScreenReader('Services are ready');
        } else {
            updateServiceBadge(false);
            announceToScreenReader('Some services may be unavailable');
        }
    } catch (error) {
        console.error('Status check failed:', error);
        updateServiceBadge(false);
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();

    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();

    if (!message) {
        announceToScreenReader('Please enter a message');
        return;
    }

    if (message.length > CONFIG.MAX_MESSAGE_LENGTH) {
        announceToScreenReader(`Message too long. Maximum ${CONFIG.MAX_MESSAGE_LENGTH} characters`);
        return;
    }

    userInput.disabled = true;
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Sending...';

    try {
        addMessage(message, true);
        userInput.value = '';
        showTypingIndicator();

        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.CHAT_ENDPOINT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                language: currentLanguage,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get response');
        }

        const data = await response.json();

        removeTypingIndicator();
        addMessage(data.response, false, data.intent);
        announceToScreenReader(`Assistant says: ${data.response.substring(0, 100)}`);

        if (data.follow_up_suggestions && data.follow_up_suggestions.length > 0) {
            displayFollowUpSuggestions(data.follow_up_suggestions);
        }

        if (data.sources && data.sources.length > 0) {
            displaySources(data.sources);
        }

        scrollToLatestMessage();

    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator();
        addMessage(`Error: ${error.message}`, false);
        announceToScreenReader(`Error: ${error.message}`);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
        userInput.focus();
    }
}

function addMessage(content, isUser, intent) {
    // Hide empty state on first message
    const emptyState = document.getElementById('empty-state');
    if (emptyState) emptyState.style.display = 'none';

    const chatMessages = document.getElementById('chat-messages');
    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const row = document.createElement('div');
    row.className = isUser ? 'message-row user-row' : 'message-row';

    const avatarEmoji = isUser ? '👤' : '🤖';
    const avatarClass = isUser ? 'user-avatar' : 'bot-avatar';
    const bubbleClass = isUser ? 'user-bubble' : 'bot-bubble';

    row.innerHTML = `
        <div class="avatar ${avatarClass}" aria-hidden="true">${avatarEmoji}</div>
        <div class="message-content">
            <div class="message-bubble ${bubbleClass}">${content}</div>
            <span class="message-time">${now}</span>
        </div>
    `;

    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Update session stats
    if (!isUser) {
        updateStats(intent);
    }
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const existing = document.getElementById('typing-indicator');
    if (existing) existing.remove();

    const row = document.createElement('div');
    row.className = 'typing-row';
    row.id = 'typing-indicator';
    row.setAttribute('aria-label', 'Assistant is typing');
    row.innerHTML = `
        <div class="avatar bot-avatar" aria-hidden="true">🤖</div>
        <div class="typing-bubble">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function formatMessageForDisplay(message) {
    const div = document.createElement('div');
    div.textContent = message;
    let formattedMessage = div.innerHTML;

    formattedMessage = formattedMessage.replace(
        /https?:\/\/[^\s]+/g,
        (url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${url}</a>`
    );

    formattedMessage = formattedMessage.replace(/\n/g, '<br>');

    return formattedMessage;
}

function displayFollowUpSuggestions(suggestions) {
    console.log('Follow-up suggestions:', suggestions);
}

function displaySources(sources) {
    const sourcesContainer = document.getElementById('sources-container');
    const sourcesList = document.getElementById('sources-list');

    if (!sourcesContainer || !sourcesList) return;

    sourcesContainer.hidden = false;
    sourcesList.innerHTML = '';

    sources.forEach(source => {
        const li = document.createElement('li');
        li.textContent = source;
        sourcesList.appendChild(li);
    });
}

function sendQuickQuestion(question) {
    const userInput = document.getElementById('user-input');
    if (userInput) {
        userInput.value = question;
        userInput.focus();
        const form = document.getElementById('chat-form');
        if (form) form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    }
}

function updateStats(intent) {
    const questionsCount = document.getElementById('questions-count');
    const topicsCount = document.getElementById('topics-count');

    if (questionsCount) {
        const current = parseInt(questionsCount.textContent) || 0;
        questionsCount.textContent = current + 1;
    }

    if (intent && topicsCount) {
        topicsSet.add(intent);
        topicsCount.textContent = topicsSet.size;
    }
}

function useSuggestion(suggestionText) {
    const userInput = document.getElementById('user-input');
    if (userInput) {
        userInput.value = suggestionText;
        userInput.focus();
        announceToScreenReader(`Suggested question: ${suggestionText}`);
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
}

function handleSuggestionKeydown(event) {
    if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        event.target.click();
    }
}



function printConversation() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) {
        announceToScreenReader('No messages to print');
        return;
    }

    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Election Assistant Conversation</title>');
    printWindow.document.write('<style>body { font-family: Arial; margin: 20px; }');
    printWindow.document.write('.message { margin: 10px 0; padding: 10px; border-radius: 5px; }');
    printWindow.document.write('.user { background-color: #e3f2fd; }');
    printWindow.document.write('.assistant { background-color: #f5f5f5; }</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<h1>Election Assistant Conversation</h1>');
    printWindow.document.write('<p>Session ID: ' + sessionId + '</p>');
    printWindow.document.write('<p>Printed: ' + new Date().toString() + '</p>');
    printWindow.document.write('<hr>');
    printWindow.document.write(chatMessages.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
    announceToScreenReader('Conversation printed');
}

async function exportPDF() {
    announceToScreenReader('Exporting conversation as PDF...');

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/export-pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                include_sources: true,
                language: currentLanguage,
            }),
        });

        if (!response.ok) {
            throw new Error('PDF export failed');
        }

        const data = await response.json();

        if (data.url) {
            const link = document.createElement('a');
            link.href = data.url;
            link.download = `election-assistant-${sessionId}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            announceToScreenReader('PDF exported successfully');
        }
    } catch (error) {
        console.error('PDF export error:', error);
        announceToScreenReader(`PDF export failed: ${error.message}`);
    }
}

function scrollToLatestMessage() {
    const chatMessages = document.getElementById('chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function announceToScreenReader(message) {
    let liveRegion = document.getElementById('sr-announce');
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'sr-announce';
        liveRegion.className = 'sr-only';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        document.body.appendChild(liveRegion);
    }
    liveRegion.textContent = message;
}
