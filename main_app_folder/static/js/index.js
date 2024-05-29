function toggleTheme() {
    var theme = document.documentElement.getAttribute("data-theme");
    if (theme === "light") {
        document.documentElement.setAttribute("data-theme", "dark");
    } else {
        document.documentElement.setAttribute("data-theme", "light");
    }
}
document.addEventListener('DOMContentLoaded', function() {
    var themeToggleButton = document.getElementById('theme-toggle-button');
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }

    const form = document.getElementById('contact-form');
    // listen for form submission
    if(form){
        form.addEventListener('submit', function(event) {
            // prevent the default form submission
            event.preventDefault();
            // collect form data
            const formData = {
                name: form.querySelector('[name="name"]').value,
                email: form.querySelector('[name="email"]').value,
                message: form.querySelector('[name="message"]').value
            };
            
            console.log('Form Data:', formData);
            
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
            // clearing the form
            form.reset();
        });
    };
});  