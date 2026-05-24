(function() {
    let leadId = null;
    let isOpen = false;
    let isStarting = false;
    let messageQueue = [];

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
        if (isOpen && !leadId && !isStarting) startChat();
    });

    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isOpen = false;
        chatWindow.classList.add('hidden');
    });

    // Chat Logic
    async function startChat() {
        isStarting = true;
        try {
            const response = await fetch(`${API_BASE}/chat/start`, { method: 'POST' });
            if (!response.ok) throw new Error("Failed to start session");
            const data = await response.json();
            leadId = data.lead_id;
            isStarting = false;
            
            // Process queued messages
            while (messageQueue.length > 0) {
                const msg = messageQueue.shift();
                processSendMessage(msg);
            }
        } catch (e) {
            console.error("LexiWidget: Error starting chat", e);
            isStarting = false;
        }
    }

    async function sendMessage() {
        const content = input.value.trim();
        if (!content) return;

        appendMessage('user', content);
        input.value = '';

        if (!leadId) {
            if (!isStarting) startChat();
            messageQueue.push(content);
            return;
        }

        processSendMessage(content);
    }

    async function processSendMessage(content) {
        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = typingId;
        typingDiv.className = 'lexi-msg lexi-msg-ai';
        typingDiv.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const formData = new FormData();
            formData.append('content', content);
            const response = await fetch(`${API_BASE}/chat/message?lead_id=${leadId}`, {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            document.getElementById(typingId)?.remove();
            appendMessage('ai', data.content || "I'm processing your request.");
        } catch (e) {
            console.error("LexiWidget: Error sending message", e);
            document.getElementById(typingId)?.remove();
            appendMessage('ai', "I'm having a bit of trouble connecting, but I'm still here! (Mock Mode: Active)");
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
