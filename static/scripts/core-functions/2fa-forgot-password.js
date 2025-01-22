document.getElementById('forgotPasswordCodeForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission

    const authCode = document.getElementById('verificationCode').value; // Use the correct ID here

    // Retrieve the temporary token from localStorage
    const temporaryToken = localStorage.getItem('forgotpasswordtoken');
    console.log(temporaryToken); // Debugging line

    if (!temporaryToken) {
        alert('No temporary token found. Please log in again.');
        return;
    }

    try {
        const response = await fetch("/auth/2fa-forgot-password", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${temporaryToken}`  // Pass token in header
            },
            body: JSON.stringify({ authCode })
        });

        const data = await response.json();
        console.log(data); // Debugging line for response data

        if (response.ok) {
            // If the response is successful, redirect to reset-password
            window.location.href = '/auth/reset-password';
        } else {
            alert(data.message || 'An error occurred during 2FA verification.');
        }
    } catch (error) {
        console.error('Error during 2FA verification:', error);
        alert('An error occurred. Please try again.');
    }
});
