/**
 * FC-Advisor - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.querySelector('.nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (e) {
            if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
            }
        });
    }

    // Auto-dismiss flash messages after 5 seconds
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(function () {
                flash.remove();
            }, 300);
        }, 5000);
    });

    // Add slide out animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(20px);
            }
        }
    `;
    document.head.appendChild(style);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to forms on submit
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';
            }
        });
    });
});
