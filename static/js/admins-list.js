function initializeAdminsGrid(adminsData) {
    const adminsGrid = document.querySelector('.admins-grid');
    
    adminsData.forEach(admin => {
        const adminElement = document.createElement('div');
        adminElement.className = 'admin-card';
        adminElement.innerHTML = `
            <div class="admin-header">
                <h3>${admin.username}</h3>
                <span class="admin-role">${admin.role}</span>
            </div>
            <div class="admin-actions">
                <button onclick="location.href='/admin/admins/edit/${admin.username}'">
                    <i class="material-icons">edit</i>
                </button>
                ${admin.username !== 'admin' ? `
                    <button onclick="deleteAdmin('${admin.username}')">
                        <i class="material-icons">delete</i>
                    </button>
                ` : ''}
            </div>
        `;
        adminsGrid.appendChild(adminElement);
    });
}

function deleteAdmin(username) {
    if (confirm('Are you sure you want to delete this administrator?')) {
        fetch(`/admin/admins/delete/${username}`, {
            method: 'DELETE'
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error deleting administrator');
            }
        });
    }
}
