document.getElementById('verifyForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const certNo = document.getElementById('certNo').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const firstName = document.getElementById('firstName').value.trim();
    
    // Redirect to verification page with all parameters
    window.location.href = `/verify/${certNo}?lastName=${encodeURIComponent(lastName)}&firstName=${encodeURIComponent(firstName)}`;
}); 