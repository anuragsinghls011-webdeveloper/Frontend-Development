// Initialize AOS with enhanced settings
AOS.init({
    duration: 1000,
    once: true,
    offset: 100,
    easing: 'ease-out'
});

// DOM Elements
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
const links = document.querySelectorAll('.nav-links a');
const header = document.querySelector('.header');
const scrollTopBtn = document.querySelector('.scroll-top');
const skillBars = document.querySelectorAll('.progress-bar');
const sections = document.querySelectorAll('section');
const themeToggle = document.querySelector('.theme-toggle');
const htmlElement = document.documentElement;

// Typed Text Configuration
const roles = [
    'Frontend Developer',
    'UI/UX Enthusiast',
    'Web Designer',
    'Problem Solver'
];

let roleIndex = 0;
let charIndex = 0;
let isDeleting = false;
let typingDelay = 200;
const erasingDelay = 100;
const newTextDelay = 2000;

// Smooth Scroll
function smoothScroll(target, duration) {
    const targetPosition = target.getBoundingClientRect().top + window.pageYOffset;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition - 70;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);
        if (timeElapsed < duration) requestAnimationFrame(animation);
    }

    function ease(t, b, c, d) {
        t /= d;
        return -c * t * (t - 2) + b;
    }

    requestAnimationFrame(animation);
}

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            smoothScroll(target, 1000);
        }
    });
});

// Typewriter Effect
function typeWriter() {
    const currentRole = roles[roleIndex];
    const typedTextElement = document.querySelector('.typed-text');
    
    if (!typedTextElement) return;

    if (isDeleting) {
        charIndex--;
        typingDelay = erasingDelay;
    } else {
        charIndex++;
        typingDelay = 200;
    }

    typedTextElement.textContent = currentRole.substring(0, charIndex);

    if (!isDeleting && charIndex === currentRole.length) {
        isDeleting = true;
        typingDelay = newTextDelay;
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
    }

    setTimeout(typeWriter, typingDelay);
}

// Mobile Navigation
hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.nav') && navLinks.classList.contains('active')) {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    }
});

// Close mobile menu when clicking on a link
links.forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});

// Scroll Events
window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Header shadow on scroll
    if (scrollTop > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
    
    // Show/hide scroll to top button
    if (scrollTop > 500) {
        scrollTopBtn.classList.add('visible');
    } else {
        scrollTopBtn.classList.remove('visible');
    }
    
    // Update active nav link based on scroll position
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.clientHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollTop >= sectionTop && scrollTop < sectionTop + sectionHeight) {
            links.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const headerOffset = 70;
            const elementPosition = target.offsetTop;
            const offsetPosition = elementPosition - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Scroll to top
scrollTopBtn.addEventListener('click', () => {
    smoothScroll(document.body, 1000);
});

// Theme Toggle
function updateThemeIcon(theme) {
    const icon = themeToggle.querySelector('i');
    icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme') || 'dark';
htmlElement.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

themeToggle.addEventListener('click', () => {
    const currentTheme = htmlElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    htmlElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Start typewriter effect
    setTimeout(typeWriter, 1000);
    
    // Remove preloader
    const preloader = document.querySelector('.preloader');
    setTimeout(() => {
        preloader.classList.add('fade-out');
    }, 500);
});

// Form Handling
const form = document.getElementById('contact-form');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    const formProps = Object.fromEntries(formData);
    
    // Add loading state to button
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    submitBtn.disabled = true;
    
    try {
        // Simulate sending email (replace with actual email service)
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Show success message
        showNotification('Message sent successfully!', 'success');
        form.reset();
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to send message. Please try again.', 'error');
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
});

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
} 