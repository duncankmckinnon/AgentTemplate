document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    
    // Add welcome message
    addMessageToChat("Hello! How can I help you today?", 'bot-message');
    
    // Generate or retrieve conversation hash
    function getConversationHash() {
        let hash = localStorage.getItem('conversationHash');
        if (!hash) {
            // Generate a random hash if none exists
            hash = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
            localStorage.setItem('conversationHash', hash);
        }
        return hash;
    }
    
    // Send message
    function sendMessage() {
        const message = messageInput.value.trim();
        const requestTimestamp = new Date().toISOString();
        const conversationHash = getConversationHash();
        
        if (!message) {
            return;
        }
        
        // Add user message to chat
        addMessageToChat(message, 'user-message');
        messageInput.value = '';
        
        // Add a typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message typing-indicator';
        typingIndicator.textContent = 'Typing...';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send message to server
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_hash: conversationHash,
                message: message,
                request_timestamp: requestTimestamp
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChat(data.response, 'bot-message');
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    // Add message to chat
    function addMessageToChat(message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.textContent = message;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
}); 