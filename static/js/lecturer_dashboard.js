// Counter handling without animation
document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        // Get the value and ensure it's valid
        const value = parseInt(counter.innerText) || 0;
        
        // Display only non-negative values
        counter.textContent = value >= 0 ? value : '0';
    });
});
