document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatbox = document.getElementById("chatbox");
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');

    function sendMessage() {
        let message = userInput.value.trim();
        if (!message) return;  // Don't send empty messages

        let userHtml = '<p class="userText"><span>' + message + '</span></p>';
        if (chatbox) {
            chatbox.innerHTML += userHtml;
        }
        userInput.value = "";  // Clear input after sending

        if (csrfTokenMeta) {
            const csrfToken = csrfTokenMeta.getAttribute('content');

            fetch('/get_response', {
                method: 'POST',
                body: JSON.stringify({ message: message }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                let botHtml = '<p class="botText"><span>' + data.message + '</span></p>';
                if (chatbox) {
                    chatbox.innerHTML += botHtml;
                    chatbox.scrollTop = chatbox.scrollHeight;
                }
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('CSRF token not found');
        }
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
                e.preventDefault();  // Prevent default form submission
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chat-widget');
    const chatIcon = document.getElementById('chatIcon');
    const minimizeChat = document.getElementById('minimizeChat');

    if (chatWidget && chatIcon) {
        if (localStorage.getItem('chatMinimized') === 'true') {
            chatIcon.style.display = 'block';
        } else {
            chatWidget.style.display = 'flex';
        }
    }

    if (minimizeChat) {
        minimizeChat.addEventListener('click', function() {
            if (chatWidget && chatIcon) {
                chatWidget.style.display = 'none';
                chatIcon.style.display = 'block';
                localStorage.setItem('chatMinimized', 'true');
            }
        });
    }

    if (chatIcon) {
        chatIcon.addEventListener('click', function() {
            if (chatWidget) {
                chatWidget.style.display = 'flex';
                chatIcon.style.display = 'none';
                localStorage.removeItem('chatMinimized');
            }
        });
    }
});
