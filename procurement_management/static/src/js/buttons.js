document.querySelectorAll('.btn-gradient').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.btn-gradient').forEach(btn => btn.classList.remove('active')); // Remove active from all buttons
        this.classList.add('active'); // Add active class to clicked button
    });
});