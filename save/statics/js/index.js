function toggleTheme() {
    var theme = document.documentElement.getAttribute("data-theme");
    if (theme === "light") {
        document.documentElement.setAttribute("data-theme", "dark");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
    }
}
document.addEventListener('DOMContentLoaded', function() {
    var themeToggleButton = document.getElementById('theme-toggle-button'); // Add this button to your HTML
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }
    // Get the form element
    const form = document.getElementById('contact-form');
    // Listen for form submission
    if(form){
        form.addEventListener('submit', function(event) {
            // Prevent the default form submission
            event.preventDefault();
            // Collect form data
            const formData = {
                name: form.querySelector('[name="name"]').value,
                email: form.querySelector('[name="email"]').value,
                message: form.querySelector('[name="message"]').value
            };
            // Log or process the form data
            console.log('Form Data:', formData);
            // Example of sending form data to a server
            fetch('/web/submit-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                alert(data.message);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
            // Optionally, clear the form
            form.reset();
        });
    };
});  