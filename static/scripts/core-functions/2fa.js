document.getElementById('2faForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission
  
    const authCode = document.getElementById('authCode').value;
  
    // Retrieve the temporary token from localStorage
    const temporaryToken = localStorage.getItem('temporary_token');  // Adjust as needed

    if (!temporaryToken) {
        alert('No temporary token found. Please log in again.');
        return;
    }

    try {
        const response = await fetch("/auth/2fa", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${temporaryToken}`  // Pass token in header
            },
            body: JSON.stringify({ authCode })
        });
        
        const data = await response.json();

        if (response.ok) {
            // If the response is successful, save the new access token
            const accessToken = data.access_token;

            if (accessToken) {
                localStorage.setItem('token', accessToken);
                localStorage.removeItem('temporary_token');
 // Store the new access token
                window.location.href = '/doctor/dashboard';
            
            // Redirect to the dashboard (or another page)
            } else {
                alert('2FA failed: No access token received.');
            }
        } else {
            alert(data.message || 'An error occurred during 2FA verification.');
        }
    } catch (error) {
        console.error('Error during 2FA verification:', error);
        alert('An error occurred. Please try again.');
    }
});
