function initializeCertificateForm(certData) {
    if (certData && Object.keys(certData).length > 0) {
        // Update form title
        document.querySelector('.content-header h1').textContent = 'Edit Certificate';
        
        // Fill form fields
        document.getElementById('cert_type_type').value = certData.cert_type.type;
        document.getElementById('cert_type_title').value = certData.cert_type.title;
        document.getElementById('cert_type_description').value = certData.cert_type.description;
        document.getElementById('owner').value = certData.owner;
        document.getElementById('birthdate').value = certData.birthdate;
        document.getElementById('address_street').value = certData.address.street;
        document.getElementById('address_no').value = certData.address.no;
        document.getElementById('address_city').value = certData.address.city;
        document.getElementById('address_zip').value = certData.address.zip;
        document.getElementById('contact_phone').value = certData.contact.phone;
        document.getElementById('contact_email').value = certData.contact.email;
        document.getElementById('expire_date').value = certData.expire_date;
        
        // Update form action
        document.getElementById('certificateForm').action = `/admin/certificates/edit/${certData.cert_number}`;
        
        // Update submit button text
        document.querySelector('.btn-primary').textContent = 'Update Certificate';
    }

    // Handle form submission
    document.getElementById('certificateForm').onsubmit = function(e) {
        e.preventDefault();
        
        // Check if we're editing (URL contains 'edit')
        const isEdit = window.location.href.includes('/edit/');
        if (isEdit) {
            // Convert form data to URL-encoded string
            const formData = new FormData(this);
            const data = new URLSearchParams(formData).toString();
            
            // Send PUT request
            fetch(window.location.href, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: data
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    window.location.href = '/admin/certificates';
                } else {
                    alert('Error updating certificate');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error updating certificate: ' + error.message);
            });
        } else {
            // For new certificates, submit normally
            this.submit();
        }
    };
}
