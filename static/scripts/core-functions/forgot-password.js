document.getElementById('forgotPasswordForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission
    const email = document.getElementById('email').value;  // Ensure you're capturing the email value correctly

    try {
        const response = await fetch("/auth/forgot-password", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email }),
        });
        
        // Parse the response data
        const data = await response.json();

        // Debugging purpose
        console.log('Full response:', data);

        if (response.ok) {
            console.log('Login successful, storing temporary token');
            
            const forgotpasswordToken = data.temporary_token;
            const message = data.message;

            // Check if the token exists
            if (forgotpasswordToken) {
                // Store the token in local storage
                localStorage.setItem('forgotpasswordtoken', forgotpasswordToken);

                // Display the success message
                alert(message); // Notify the user

                // Redirect to the 2FA page
                window.location.href = '/auth/2fa-forgot-password';
            } else {
                alert('Login successful but no token received.');
            }
        } else {
            // In case of an error response (not ok)
            alert(data.message || 'An error occurred during email sending');
        }
    } catch (error) {
        console.error('Error during email sending', error);
        alert('An error occurred. Please try again.');
    }
});
