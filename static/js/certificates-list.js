// Initialize certificates grid
function initializeCertificatesGrid(certificatesData) {
    const certificatesGrid = document.querySelector('.certificates-grid');
    
    certificatesData.forEach(cert => {
        const expireDate = new Date(cert.expire_date);
        const isExpired = expireDate < new Date();
        
        const certElement = document.createElement('div');
        certElement.className = `certificate-card ${isExpired ? 'expired' : ''}`;
        certElement.innerHTML = `
            <div class="cert-header">
                <h3>${cert.owner}</h3>
                <span class="cert-number">#${cert.cert_number}</span>
            </div>
            <div class="cert-details">
                <p><strong>Type:</strong> ${cert.cert_type.type}</p>
                <p><strong>Expires:</strong> ${cert.expire_date}</p>
            </div>
            <div class="cert-actions">
                <button onclick="location.href='/admin/certificates/edit/${cert.cert_number}'">
                    <i class="material-icons">edit</i>
                </button>
                <button onclick="deleteCertificate('${cert.cert_number}')">
                    <i class="material-icons">delete</i>
                </button>
            </div>
        `;
        certificatesGrid.appendChild(certElement);
    });
}

function deleteCertificate(certNumber) {
    if (confirm('Are you sure you want to delete this certificate?')) {
        fetch(`/admin/certificates/delete/${certNumber}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting certificate');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting certificate: ' + error.message);
        });
    }
}
