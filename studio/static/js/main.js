// Initialize Bootstrap tooltips
document.addEventListener('DOMContentLoaded', function() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Lightbox initialization for portfolio images
    const lightbox = GLightbox({
        selector: '.glightbox'
    });
    
    // Booking calendar initialization
    const bookingCalendar = flatpickr("#booking-date", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        minDate: "today",
        disable: [
            function(date) {
                // Disable Sundays
                return (date.getDay() === 0);
            }
        ]
    });
    
    // Coupon code validation
    document.getElementById('apply-coupon').addEventListener('click', function() {
        const couponCode = document.getElementById('coupon-code').value;
        // AJAX request to validate coupon
        fetch(`/validate-coupon/?code=${couponCode}`)
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    // Update price display
                    document.getElementById('final-price').textContent = data.discounted_price;
                    document.getElementById('discount-message').textContent = 
                        `Discount applied: ${data.discount_percent}% off!`;
                } else {
                    alert('Invalid coupon code');
                }
            });
    });
});