document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    // Function to handle sending messages
    function sendMessage() {
        let message = userInput.value.trim();
        if (message === '') return;  // Don't send empty messages

        // Append user message to chat
        let userHtml = '<p class="userText"><span>' + message + '</span></p>';
        document.getElementById("chatbox").innerHTML += userHtml;
        userInput.value = "";  // Clear input after sending

        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        // Send message to server and handle response
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
            document.getElementById("chatbox").innerHTML += botHtml;
            document.getElementById('chatbox').scrollTop = document.getElementById('chatbox').scrollHeight;
        })
        .catch(error => console.error('Error:', error));
    }

    // Event listener for the send button
    sendBtn.addEventListener('click', sendMessage);

    // Event listener for the enter key in the text input field
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
            e.preventDefault();  // Prevent the default action to stop from submitting the form
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chat-widget');
    const chatIcon = document.getElementById('chatIcon');

    // Initially hide the chat widget and icon
    chatWidget.style.display = 'none';
    chatIcon.style.display = 'none';

    // Check localStorage and adjust visibility
    if (localStorage.getItem('chatMinimized') === 'true') {
        chatIcon.style.display = 'block';  // Show only the icon if minimized
    } else {
        chatWidget.style.display = 'flex';  // Show the chat widget if not minimized
    }

    document.getElementById('minimizeChat').addEventListener('click', function() {
        chatWidget.style.display = 'none';
        chatIcon.style.display = 'block';
        localStorage.setItem('chatMinimized', 'true');
    });

    chatIcon.addEventListener('click', function() {
        chatWidget.style.display = 'flex';
        chatIcon.style.display = 'none';
        localStorage.removeItem('chatMinimized');
    });
});
