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

function setupEventListeners() {
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleFormSubmit);
    }

    const voiceBtn = document.getElementById('voice-input-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleVoiceInput);
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

async function checkServiceStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.STATUS_ENDPOINT}`);
        const data = await response.json();

        const badge = document.getElementById('service-badge');
        if (badge) {
            if (response.ok) {
                badge.textContent = '✓ Services Ready';
                badge.classList.add('status-ready');
                announceToScreenReader('Services are ready');
            } else {
                badge.textContent = '⚠ Service Issues';
                badge.classList.add('status-error');
                announceToScreenReader('Some services may be unavailable');
            }
        }
    } catch (error) {
        console.error('Status check failed:', error);
        const badge = document.getElementById('service-badge');
        if (badge) {
            badge.textContent = '✗ Service Offline';
            badge.classList.add('status-error');
        }
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
        addMessageToChat('user', message);
        userInput.value = '';

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

        addMessageToChat('assistant', data.response);
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
        addMessageToChat('system', `Error: ${error.message}`);
        announceToScreenReader(`Error: ${error.message}`);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
        userInput.focus();
    }
}

function addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.setAttribute('role', 'article');

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (sender === 'assistant') {
        contentDiv.innerHTML = formatMessageForDisplay(message);
    } else {
        contentDiv.textContent = message;
    }

    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);

    const timestamp = new Date().toLocaleTimeString();
    const timeSpan = document.createElement('span');
    timeSpan.className = 'sr-only';
    timeSpan.textContent = `${sender === 'user' ? 'You' : 'Assistant'} at ${timestamp}`;
    messageDiv.appendChild(timeSpan);
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

function checkVoiceSupport() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionSupported = !!SpeechRecognition;

    const voiceBtn = document.getElementById('voice-input-btn');
    if (!recognitionSupported && voiceBtn) {
        voiceBtn.disabled = true;
        voiceBtn.title = 'Voice input is not supported in your browser';
    }
}

function toggleVoiceInput() {
    if (!recognitionSupported) {
        announceToScreenReader('Voice input is not supported in your browser');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = currentLanguage === 'es' ? 'es-ES' : 'en-US';
    recognition.continuous = false;
    recognition.interimResults = true;

    const voiceBtn = document.getElementById('voice-input-btn');
    const userInput = document.getElementById('user-input');

    recognition.onstart = function() {
        isListening = true;
        if (voiceBtn) {
            voiceBtn.textContent = '🎤 Listening...';
            voiceBtn.classList.add('listening');
        }
        announceToScreenReader('Voice input started. Speak your question.');
    };

    recognition.onresult = function(event) {
        let interimTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;

            if (event.results[i].isFinal) {
                userInput.value = transcript;
                document.getElementById('chat-form').dispatchEvent(new Event('submit'));
            } else {
                interimTranscript += transcript;
            }
        }
    };

    recognition.onerror = function(event) {
        console.error('Voice input error:', event.error);
        announceToScreenReader(`Voice input error: ${event.error}`);
    };

    recognition.onend = function() {
        isListening = false;
        if (voiceBtn) {
            voiceBtn.textContent = '🎤 Voice Input';
            voiceBtn.classList.remove('listening');
        }
        announceToScreenReader('Voice input ended');
    };

    recognition.start();
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
