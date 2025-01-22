document.getElementById('loginForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission
  
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
  
    try {
        const response = await fetch("/auth/login", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        // Parse the response data
        const data = await response.json();

        // Debugging purpose
        console.log('Full response:', data);

        if (response.ok) {
            console.log('Login successful, storing temporary token');
            
            const temporaryToken = data.temporary_token;
            const message = data.message;

            // Check if the token exists
            if (temporaryToken) {
                // Store the token in local storage
                localStorage.setItem('temporary_token', temporaryToken);

                // Display the success message
                alert(message); // Notify the user

                // Redirect to the 2FA page
                window.location.href = '/auth/2fa';
            } else {
                alert('Login successful but no token received.');
            }
        } else {
            // In case of an error response (not ok)
            alert(data.message || 'An error occurred during login');
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred. Please try again.');
    }
});
