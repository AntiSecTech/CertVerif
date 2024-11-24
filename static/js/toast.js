function showToast(message, type = 'default') {
    const toast = document.getElementById('toast');
    toast.className = `toast show ${type}`;
    toast.textContent = message;

    setTimeout(function(){ 
        toast.className = toast.className.replace('show', '');
    }, 3000);
}
