function initializeAdminForm(adminData) {
    if (adminData && Object.keys(adminData).length > 0) {
        // Update form title
        document.getElementById('formTitle').textContent = 'Edit Admin';
        
        // Fill form fields
        if (adminData.username) {
            const usernameInput = document.getElementById('username');
            usernameInput.value = adminData.username;
            usernameInput.readOnly = true;
        }
        
        if (adminData.role) {
            document.getElementById('role').value = adminData.role;
        }
        
        // Update form action
        document.getElementById('adminForm').action = `/admin/admins/edit/${adminData.username}`;
        
        // Password is optional in edit mode
        document.getElementById('password').required = false;
    }

    // Handle form submission
    document.getElementById('adminForm').onsubmit = function(e) {
        e.preventDefault();
        
        // Basic validation
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        if (!username) {
            document.getElementById('username-error').textContent = 'Username is required';
            return;
        }
        
        // Password is required only for new admins
        if (!adminData.username && !password) {
            document.getElementById('password-error').textContent = 'Password is required';
            return;
        }
        
        // Clear any previous error messages
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
        
        // Check if we're editing
        const isEdit = window.location.href.includes('/edit/');
        if (isEdit) {
            handleEditSubmission(this);
        } else {
            // For new admins, submit normally
            this.submit();
        }
    };
}

function handleEditSubmission(form) {
    const formData = new FormData(form);
    const data = new URLSearchParams(formData).toString();
    
    fetch(window.location.href, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRF-Token': document.querySelector('input[name="csrf_token"]').value
        },
        body: data
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            window.location.href = '/admin/admins';
        } else {
            alert('Error updating admin');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating admin: ' + error.message);
    });
} 