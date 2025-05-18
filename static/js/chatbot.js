document.addEventListener('DOMContentLoaded', () => {
    const chatbotContainer = document.createElement('div');
    chatbotContainer.id = 'chatbot-container';
    // Add an icon placeholder in the header
    chatbotContainer.innerHTML = `
        <div id="chatbot-header">
            <div class="chatbot-header-content">
                 <i class="fas fa-robot chatbot-avatar"></i> <!-- Bot avatar icon -->
                 <span>AI Assistant</span>
            </div>
            <button id="chatbot-toggle-btn">-</button> <!-- Use '-' for minimize initially -->
        </div>
        <div id="chatbot-body">
            <ul id="chatbot-messages">
                <li class="chatbot-message bot">Hello! How can I help you today?</li>
            </ul>
            <div id="chatbot-input-area">
                <input type="text" id="chatbot-input" placeholder="Type your message...">
                <button id="chatbot-send-btn">Send</button>
            </div>
        </div>
    `;
    document.body.appendChild(chatbotContainer);

    const messagesList = document.getElementById('chatbot-messages');
    const inputField = document.getElementById('chatbot-input');
    const sendButton = document.getElementById('chatbot-send-btn');
    const chatBody = document.getElementById('chatbot-body');
    const toggleButton = document.getElementById('chatbot-toggle-btn');
    const chatHeader = document.getElementById('chatbot-header');

    let isMinimized = false;

    // --- Helper Functions ---
    function addMessage(text, sender) {
        const messageItem = document.createElement('li');
        messageItem.classList.add('chatbot-message', sender); // sender is 'user' or 'bot'

        // Sanitize text before adding to prevent XSS
        const textNode = document.createTextNode(text);
        messageItem.appendChild(textNode);

        messagesList.appendChild(messageItem);
        scrollToBottom();
    }

    function addLoadingIndicator() {
        const loadingItem = document.createElement('li');
        loadingItem.classList.add('chatbot-message', 'bot', 'loading');
        loadingItem.innerHTML = '<span></span><span></span><span></span>'; // Dots
        loadingItem.id = 'loading-indicator'; // Give it an ID to remove later
        messagesList.appendChild(loadingItem);
        scrollToBottom();
    }

    function removeLoadingIndicator() {
        const indicator = document.getElementById('loading-indicator');
        if (indicator) {
            messagesList.removeChild(indicator);
        }
    }

    function scrollToBottom() {
        // Scroll the chat body, not the messages list itself
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    async function sendMessage() {
        const messageText = inputField.value.trim();
        if (!messageText) return; // Don't send empty messages

        addMessage(messageText, 'user');
        inputField.value = ''; // Clear input field
        sendButton.disabled = true; // Disable button while waiting
        addLoadingIndicator();

        try {
            // Get the CSRF token (important if not using @csrf_exempt)
            // const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // Updated endpoint URL to match our new OpenRouter view
            const response = await fetch('/chatbot/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // Include CSRF token if needed:
                    // 'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: messageText })
            });

            removeLoadingIndicator();

            if (!response.ok) {
                // Try to get error message from response, otherwise use status text
                let errorMsg = `Error: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* Ignore if response is not JSON */ }
                
                // Specific handling for rate limiting
                if (response.status === 429) {
                    errorMsg = 'Rate limit exceeded. Please try again in a moment.';
                }
                
                addMessage(errorMsg, 'bot');
                console.error('Chatbot API error:', response.status, errorMsg);
            } else {
                const data = await response.json();
                addMessage(data.reply, 'bot');
            }

        } catch (error) {
            removeLoadingIndicator();
            addMessage('Sorry, something went wrong. Please try again.', 'bot');
            console.error('Error sending message:', error);
        } finally {
             sendButton.disabled = false; // Re-enable button
             inputField.focus(); // Keep focus on input
        }
    }

    // --- Event Listeners ---
    sendButton.addEventListener('click', sendMessage);

    inputField.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Toggle chat window visibility
    chatHeader.addEventListener('click', (event) => {
        // Prevent toggling if the click was on the button itself
        if (event.target.id === 'chatbot-toggle-btn') return;

        isMinimized = !isMinimized;
        chatBody.classList.toggle('hidden', isMinimized);
        toggleButton.textContent = isMinimized ? '+' : '-'; // Change button icon
        chatbotContainer.style.maxHeight = isMinimized ? '50px' : '500px'; // Adjust container height
    });
    
    // Separate listener for the button to ensure it always works
    toggleButton.addEventListener('click', () => {
        isMinimized = !isMinimized;
        chatBody.classList.toggle('hidden', isMinimized);
        toggleButton.textContent = isMinimized ? '+' : '-';
        chatbotContainer.style.maxHeight = isMinimized ? '50px' : '500px';
    });

    // Initial scroll to bottom if there are messages
    scrollToBottom();
});