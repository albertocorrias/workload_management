let slideIndex = 0;
let slideTimeout;
const slides = document.getElementsByClassName("slide");
const dots = document.getElementsByClassName("dot");

// Start initial automatic countdown loop
resetTimeout();

function moveSlide(n) {
    updateSlideIndex(slideIndex + n);
}

function currentSlide(n) {
    updateSlideIndex(n);
}

// Separate state changes from display rendering 
function updateSlideIndex(newIndex) {
    // Clear automated background logic loop timers
    clearTimeout(slideTimeout);

    // Global correction of layout boundaries
    if (newIndex >= slides.length) { newIndex = 0; }
    if (newIndex < 0) { newIndex = slides.length - 1; }

    // Toggle active state classes instantly without blocking display styles
    slides[slideIndex].classList.remove("active");
    dots[slideIndex].classList.remove("active");

    slideIndex = newIndex;

    slides[slideIndex].classList.add("active");
    dots[slideIndex].classList.add("active");

    // Queue next transition steps
    resetTimeout();
}

function resetTimeout() {
    slideTimeout = setTimeout(() => {
        updateSlideIndex(slideIndex + 1);
    }, 3000); // 3 seconds interval
}
