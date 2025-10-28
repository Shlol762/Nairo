document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const promptInput = document.getElementById('prompt-input');
    const sendButton = document.getElementById('send-button');
    const chatHistory = document.getElementById('chat-history');
    const loadingIndicator = document.getElementById('loading-indicator');
    const statusIndicator = document.getElementById('status-indicator');

    const CORE_SERVER_URL = '/api/prompt'; // Use relative path since it's served by Flask

    // --- Helper Functions ---

    function addMessageToHistory(sender, message) {
        const messageDiv = document.createElement('div');
        const bubble = document.createElement('div');
        
        bubble.classList.add('p-3', 'rounded-lg', 'max-w-xs', 'md:max-w-md', 'text-sm');
        
        if (sender === 'user') {
            messageDiv.classList.add('flex', 'justify-end');
            bubble.classList.add('chat-bubble-user');
        } else {
            messageDiv.classList.add('flex', 'justify-start');
            bubble.classList.add('chat-bubble-ai');
        }
        
        // Basic Markdown-like formatting for newlines
        bubble.innerHTML = message.replace(/\n/g, '<br>');
        
        messageDiv.appendChild(bubble);
        chatHistory.appendChild(messageDiv);
        
        // Scroll to bottom
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function setLoading(isLoading) {
        if (isLoading) {
            loadingIndicator.classList.remove('hidden');
            sendButton.disabled = true;
            promptInput.disabled = true;
        } else {
            loadingIndicator.classList.add('hidden');
            sendButton.disabled = false;
            promptInput.disabled = false;
            promptInput.focus();
        }
    }

    // --- Check Server Status ---
    async function checkStatus() {
        try {
            // We just check if the root endpoint is alive
            const response = await fetch('/', { method: 'HEAD', timeout: 2000 });
            if (response.ok) {
                statusIndicator.classList.remove('bg-red-500');
                statusIndicator.classList.add('bg-green-500');
                statusIndicator.title = 'Online';
            } else {
                throw new Error('Server not OK');
            }
        } catch (error) {
            statusIndicator.classList.remove('bg-green-500');
            statusIndicator.classList.add('bg-red-500');
            statusIndicator.title = 'Offline';
        }
    }

    // --- Form Submission ---
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        addMessageToHistory('user', prompt);
        setLoading(true);
        promptInput.value = '';

        try {
            const response = await fetch(CORE_SERVER_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: 'web_ui',
                    prompt: prompt,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            addMessageToHistory('ai', data.response);

        } catch (error) {
            console.error('Error sending command:', error);
            addMessageToHistory('ai', `Sorry, I encountered an error: \n${error.message}`);
            checkStatus(); // Re-check status if a request fails
        } finally {
            setLoading(false);
        }
    });

    // --- Initial Check ---
    checkStatus();
    // Check status every 10 seconds
    setInterval(checkStatus, 10000); 
});
