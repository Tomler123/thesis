document.getElementById('sendBtn').addEventListener('click', function() {
    let userInput = document.getElementById('userInput').value;
    if (userInput.trim() === '') return; // Prevent sending empty messages

    let userHtml = '<p class="userText"><span>' + userInput + '</span></p>';
    document.getElementById("chatbox").innerHTML += userHtml;
    document.getElementById('userInput').value = ""; // Clear input after sending

    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    fetch('/get_response', {
        method: 'POST',
        body: JSON.stringify({ message: userInput }),
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
});


document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chat-widget');
    const chatIcon = document.getElementById('chatIcon');
    const minimizeChat = document.getElementById('minimizeChat');

    // Check localStorage for the chat's state and update the display accordingly
    if (localStorage.getItem('chatMinimized') === 'true') {
        chatWidget.style.display = 'none';
        chatIcon.style.display = 'block';
    } else {
        chatWidget.style.display = 'flex';  // Initially closed, change to 'none' if you want it open
        chatIcon.style.display = 'none';
    }

    minimizeChat.addEventListener('click', function() {
        if (chatWidget.style.display !== 'none') {
            chatWidget.style.display = 'none';
            chatIcon.style.display = 'block';
            localStorage.setItem('chatMinimized', 'true');  // Save state as minimized
        }
    });

    chatIcon.addEventListener('click', function() {
        chatWidget.style.display = 'flex';
        chatIcon.style.display = 'none';
        localStorage.removeItem('chatMinimized');  // Remove minimized state
    });
});