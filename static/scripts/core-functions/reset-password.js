document.getElementById('resetPasswordForm').addEventListener('submit', async function (event) {
    event.preventDefault();
  
    // Retrieve the new password input field and its value
    const newPassword = document.getElementById('newPassword').value.trim();  // Get the value, not the element
    
    console.log('New Password:', newPassword);  // Log the new password value
  
    // Retrieve the JWT token from localStorage
    const token = localStorage.getItem('forgotpasswordtoken');
  
    console.log('Forgot Password Token:', token);  // Debugging log
  
    if (!token) {
        alert('Authorization token missing. Please log in again.');
        return;
    }
  
    try {
        const response = await fetch('/auth/reset-password', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ new_password: newPassword }),  // Send the password value, not the element
        });
  
        if (response.ok) {
            alert('Password updated successfully. Please log in.');
            window.location.href = '/auth/login';
        } else {
            const errorData = await response.json();
            alert(errorData.message || 'Failed to update password. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An unexpected error occurred. Please try again later.');
    }
});
