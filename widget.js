(function() {
    let leadId = null;
    let isOpen = false;

    // Create Widget HTML
    const container = document.createElement('div');
    container.id = 'lexi-widget-container';
    container.innerHTML = `
        <div id="lexi-chat-window" class="hidden">
            <div id="lexi-chat-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <i class="bi bi-briefcase-fill"></i>
                    <span style="font-weight: 600;">LexiFlow Assistant</span>
                </div>
                <button id="lexi-chat-close" style="background: none; border: none; color: white; cursor: pointer;">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
            <div id="lexi-chat-messages">
                <div class="lexi-msg lexi-msg-ai">Hello! I'm Lexi, your AI assistant. How can I help you today?</div>
            </div>
            <div id="lexi-chat-input-container">
                <input type="text" id="lexi-chat-input" placeholder="Type a message...">
                <button id="lexi-chat-send">
                    <i class="bi bi-send-fill"></i>
                </button>
            </div>
        </div>
        <div id="lexi-widget-button">
            <i class="bi bi-chat-fill" style="font-size: 24px;"></i>
        </div>
    `;
    document.body.appendChild(container);

    // Elements
    const button = document.getElementById('lexi-widget-button');
    const chatWindow = document.getElementById('lexi-chat-window');
    const closeBtn = document.getElementById('lexi-chat-close');
    const sendBtn = document.getElementById('lexi-chat-send');
    const input = document.getElementById('lexi-chat-input');
    const messagesContainer = document.getElementById('lexi-chat-messages');

    // Toggle Chat
    button.addEventListener('click', () => {
        isOpen = !isOpen;
        chatWindow.classList.toggle('hidden');
        if (isOpen && !leadId) startChat();
    });

    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isOpen = false;
        chatWindow.classList.add('hidden');
    });

    // Chat Logic
    async function startChat() {
        try {
            const response = await fetch(`${API_BASE}/chat/start`, { method: 'POST' });
            const data = await response.json();
            leadId = data.lead_id;
        } catch (e) {
            console.error("LexiWidget: Error starting chat", e);
        }
    }

    async function sendMessage() {
        const content = input.value.trim();
        if (!content) return;

        appendMessage('user', content);
        input.value = '';

        try {
            const formData = new FormData();
            formData.append('content', content);
            const response = await fetch(`${API_BASE}/chat/message?lead_id=${leadId}`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            appendMessage('ai', data.content);
        } catch (e) {
            console.error("LexiWidget: Error sending message", e);
            appendMessage('ai', "I'm sorry, I'm having trouble connecting right now. Please try again later.");
        }
    }

    function appendMessage(role, content) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `lexi-msg lexi-msg-${role}`;
        msgDiv.innerText = content;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Event Listeners
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

})();
