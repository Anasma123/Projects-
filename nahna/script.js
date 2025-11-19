// Preloader functionality
document.addEventListener('DOMContentLoaded', function() {
    const preloader = document.getElementById('preloader');
    const mainContent = document.getElementById('main-content');
    const surpriseMessage = document.getElementById('surprise-message');
    
    // Add special effect to preloader text
    const preloaderText = preloader.querySelector('p');
    if (preloaderText) {
        // Make text more emotional
        preloaderText.innerHTML = "Preparing the most beautiful birthday surprise for Nahna...";
        
        // Add typing effect
        const text = preloaderText.innerHTML;
        preloaderText.innerHTML = "";
        let i = 0;
        const typing = setInterval(() => {
            if (i < text.length) {
                preloaderText.innerHTML += text.charAt(i);
                i++;
            } else {
                clearInterval(typing);
            }
        }, 50);
    }
    
    // Hide preloader and show surprise message after 5 seconds for more dramatic effect
    setTimeout(function() {
        preloader.style.opacity = '0';
        // Add special animation to preloader
        preloader.style.transform = 'scale(1.2)';
        setTimeout(function() {
            preloader.classList.add('hidden');
            
            // Show surprise message
            surpriseMessage.classList.remove('hidden');
            
            // Create initial confetti explosion
            createConfettiExplosion();
            
            // Create hearts around the surprise message
            for (let i = 0; i < 10; i++) {
                setTimeout(createHearts, i * 300);
            }
        }, 500);
    }, 5000);
    
    // Close surprise message and show main content
    const closeSurprise = document.getElementById('close-surprise');
    if (closeSurprise) {
        closeSurprise.addEventListener('click', function() {
            surpriseMessage.style.animation = 'surpriseFadeOut 0.5s ease-out forwards';
            setTimeout(function() {
                surpriseMessage.classList.add('hidden');
                mainContent.classList.remove('hidden');
                
                // Trigger entrance animations
                triggerEntranceAnimations();
                
                // Create confetti when showing main content
                createConfetti();
            }, 500);
        });
    }
});

// Wish button functionality
    const wishButton = document.getElementById('wish-button');
    if (wishButton) {
        wishButton.addEventListener('click', function() {
            // Add animation effect to button
            this.classList.add('clicked');
            
            // Create confetti effect
            createConfetti();
            
            // Scroll to wishes section with delay for confetti effect
            setTimeout(() => {
                document.querySelector('.birthday-wishes').scrollIntoView({
                    behavior: 'smooth'
                });
            }, 1000);
            
            setTimeout(() => {
                this.classList.remove('clicked');
            }, 1000);
        });
    }
    
    // Initialize countdown timer
    initializeCountdown();
    
    // Add scroll animations
    window.addEventListener('scroll', handleScrollAnimations);

// Trigger entrance animations when content loads
function triggerEntranceAnimations() {
    // Add animation classes to elements
    const animatedElements = document.querySelectorAll('.gallery-item, .wish-card, .timer-item');
    animatedElements.forEach((el, index) => {
        setTimeout(() => {
            el.classList.add('animate');
        }, index * 200);
    });
    
    // Add floating animation to cake
    const cake = document.querySelector('.cake');
    if (cake) {
        cake.style.animation = 'float 3s ease-in-out infinite';
    }
    
    // Special effect for Nahna's name
    const friendName = document.querySelector('.friend-name');
    if (friendName) {
        // Make Nahna's name extra special
        setTimeout(() => {
            friendName.style.animation = 'bounce 1s, friendNameGlow 1s infinite alternate, nameSpecialEffect 2s infinite';
            createHearts();
            createConfetti();
        }, 2000);
    }
}

// Special animation for Nahna's name
function nameSpecialEffect() {
    const friendName = document.querySelector('.friend-name');
    if (friendName) {
        // Create a special effect around Nahna's name
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                createSparkles(
                    friendName.getBoundingClientRect().left + Math.random() * friendName.offsetWidth,
                    friendName.getBoundingClientRect().top + Math.random() * friendName.offsetHeight
                );
            }, i * 100);
        }
    }
}

// Handle scroll animations
function handleScrollAnimations() {
    const elements = document.querySelectorAll('.section-title, .message-container, .countdown');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (elementPosition < screenPosition) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
    
    // Handle gallery item animations on scroll
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryItems.forEach((item, index) => {
        const itemPosition = item.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.3;
        
        if (itemPosition < screenPosition) {
            // Add staggered animation delays
            setTimeout(() => {
                item.classList.add('animate');
            }, index * 150);
        }
    });
}

// Initialize countdown timer for next birthday
function initializeCountdown() {
    // Set the next birthday date (November 20th of next year)
    const now = new Date();
    const currentYear = now.getFullYear();
    const nextBirthday = new Date(currentYear, 10, 20); // Month is 0-indexed
    
    // If birthday has passed this year, set for next year
    if (now > nextBirthday) {
        nextBirthday.setFullYear(currentYear + 1);
    }
    
    // Update the countdown every second
    const countdownInterval = setInterval(() => {
        const now = new Date().getTime();
        const distance = nextBirthday.getTime() - now;
        
        // Calculate days, hours, minutes and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        
        // Display the results
        document.getElementById('days').innerText = days.toString().padStart(2, '0');
        document.getElementById('hours').innerText = hours.toString().padStart(2, '0');
        document.getElementById('minutes').innerText = minutes.toString().padStart(2, '0');
        document.getElementById('seconds').innerText = seconds.toString().padStart(2, '0');
        
        // If the countdown is finished, display a message
        if (distance < 0) {
            clearInterval(countdownInterval);
            document.querySelector('.timer').innerHTML = "<h3>Happy Birthday! 🎉</h3>";
        }
    }, 1000);
}

// Add confetti effect on special interactions
function createConfetti() {
    const confettiContainer = document.createElement('div');
    confettiContainer.className = 'confetti-container';
    document.body.appendChild(confettiContainer);
    
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffbe0b', '#fb5607', '#ff006e'];
    
    for (let i = 0; i < 150; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
        confetti.style.width = Math.random() * 10 + 5 + 'px';
        confetti.style.height = Math.random() * 10 + 5 + 'px';
        confettiContainer.appendChild(confetti);
        
        // Animate confetti
        const animation = confetti.animate([
            { top: '-10%', transform: 'translateX(0) rotate(0deg)', opacity: 1 },
            { top: '100%', transform: `translateX(${Math.random() * 100 - 50}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
        ], {
            duration: Math.random() * 3000 + 2000,
            easing: 'cubic-bezier(0.1, 0.8, 0.2, 1)'
        });
        
        // Remove confetti after animation
        animation.onfinish = () => confetti.remove();
    }
    
    // Remove container after animation
    setTimeout(() => {
        confettiContainer.remove();
    }, 5000);
}

// Add special effects to interactive elements
document.addEventListener('click', function(e) {
    // Create ripple effect on clicks
    createRipple(e);
    
    // Create confetti on special buttons
    if (e.target.closest('.cta-button')) {
        createConfetti();
        // Add special heart effect
        createHearts();
    }
    
    // Add special effect to wish cards
    if (e.target.closest('.wish-card')) {
        const card = e.target.closest('.wish-card');
        card.style.animation = 'none';
        setTimeout(() => {
            card.style.animation = 'float 3s ease-in-out infinite';
        }, 10);
        
        // Add temporary highlight effect
        card.style.boxShadow = '0 0 30px rgba(255, 107, 107, 0.8)';
        setTimeout(() => {
            card.style.boxShadow = '';
        }, 1000);
        
        // Add special effect
        createSparkles(e.clientX, e.clientY);
    }
    
    // Add effect to gallery items
    if (e.target.closest('.gallery-item')) {
        const galleryItem = e.target.closest('.gallery-item');
        galleryItem.classList.add('animate');
        createSparkles(e.clientX, e.clientY);
        
        // Add temporary love effect
        setTimeout(() => {
            galleryItem.classList.remove('animate');
        }, 2000);
        
        // Prevent event from bubbling up
        e.stopPropagation();
    }
    
    // Add effect to timer items
    if (e.target.closest('.timer-item')) {
        createFloatingEmojis(e.clientX, e.clientY, '🎉');
    }
});

// Add mousemove effects
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', function(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    
    // Create occasional sparkles
    if (Math.random() < 0.02) {
        createSparkles(mouseX, mouseY);
    }
});

// Add special effects on scroll
window.addEventListener('scroll', function() {
    // Create occasional hearts while scrolling
    if (Math.random() < 0.1) {
        createHearts();
    }
    
    // Special effect for Nahna when scrolling to message section
    const messageSection = document.querySelector('.animated-message');
    if (messageSection) {
        const rect = messageSection.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            // When Nahna scrolls to the message, create special effects
            if (Math.random() < 0.3) {
                createFloatingEmojis(Math.random() * window.innerWidth, window.innerHeight, '🎂');
            }
        }
    }
});

// Cut cake functionality
document.addEventListener('DOMContentLoaded', function() {
    const cutCakeBtn = document.getElementById('cut-cake-btn');
    const knife = document.getElementById('knife');
    const cakeMessage = document.getElementById('cake-message');
    const interactiveCake = document.getElementById('interactive-cake');
    
    if (cutCakeBtn) {
        cutCakeBtn.addEventListener('click', function() {
            // Add cutting animation
            knife.classList.add('cut');
            
            // Show message after delay
            setTimeout(() => {
                cakeMessage.classList.add('show');
                
                // Create confetti
                createConfetti();
                
                // Create hearts
                createHearts();
                
                // Change button text
                this.textContent = 'Enjoy the Cake!';
                this.disabled = true;
            }, 1000);
        });
    }
    
    // Also allow clicking on the cake to cut it
    if (interactiveCake) {
        interactiveCake.addEventListener('click', function() {
            if (knife && !knife.classList.contains('cut')) {
                knife.classList.add('cut');
                
                // Show message after delay
                setTimeout(() => {
                    if (cakeMessage) cakeMessage.classList.add('show');
                    
                    // Create confetti
                    createConfetti();
                    
                    // Create hearts
                    createHearts();
                    
                    // Change button text if it exists
                    if (cutCakeBtn) {
                        cutCakeBtn.textContent = 'Enjoy the Cake!';
                        cutCakeBtn.disabled = true;
                    }
                }, 1000);
            }
        });
    }
});

// Create ripple effect on click
function createRipple(event) {
    const button = event.target.closest('button');
    if (!button) return;
    
    const circle = document.createElement('span');
    circle.classList.add('ripple');
    circle.style.width = circle.style.height = Math.max(button.offsetWidth, button.offsetHeight) + 'px';
    circle.style.left = event.offsetX - circle.offsetWidth/2 + 'px';
    circle.style.top = event.offsetY - circle.offsetHeight/2 + 'px';
    button.appendChild(circle);
    
    // Remove ripple after animation
    setTimeout(() => {
        circle.remove();
    }, 600);
}

// Add mouse move parallax effect
document.addEventListener('mousemove', (e) => {
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;
    
    // Apply subtle parallax to hero elements
    const heroTitle = document.querySelector('.animated-title');
    if (heroTitle) {
        heroTitle.style.transform = `translate(${mouseX * 10}px, ${mouseY * 10}px)`;
    }
    
    const cake = document.querySelector('.cake');
    if (cake) {
        cake.style.transform = `translate(${mouseX * 5}px, ${mouseY * 5}px) rotateY(${mouseX * 20}deg)`;
    }
});

// Create sparkles effect
function createSparkles(x, y) {
    const sparkleContainer = document.createElement('div');
    sparkleContainer.className = 'sparkle-container';
    sparkleContainer.style.position = 'fixed';
    sparkleContainer.style.left = (x - 50) + 'px';
    sparkleContainer.style.top = (y - 50) + 'px';
    sparkleContainer.style.pointerEvents = 'none';
    sparkleContainer.style.zIndex = '9999';
    document.body.appendChild(sparkleContainer);
    
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#ffbe0b', '#fb5607', '#ff006e', '#ffd700'];
    
    for (let i = 0; i < 15; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.position = 'absolute';
        sparkle.style.width = Math.random() * 8 + 4 + 'px';
        sparkle.style.height = sparkle.style.width;
        sparkle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        sparkle.style.borderRadius = '50%';
        sparkle.style.left = '50px';
        sparkle.style.top = '50px';
        sparkle.style.opacity = '0';
        sparkleContainer.appendChild(sparkle);
        
        // Animate sparkle
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 50 + 30;
        const duration = Math.random() * 1000 + 1000;
        
        const animation = sparkle.animate([
            { opacity: 1, transform: 'translate(0, 0) scale(1)' },
            { opacity: 0, transform: `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) scale(0)` }
        ], {
            duration: duration,
            easing: 'cubic-bezier(0.1, 0.8, 0.2, 1)'
        });
        
        animation.onfinish = () => sparkle.remove();
    }
    
    // Remove container after animation
    setTimeout(() => {
        sparkleContainer.remove();
    }, 2000);
}

// Create hearts effect
function createHearts() {
    const heartContainer = document.createElement('div');
    heartContainer.className = 'heart-container';
    heartContainer.style.position = 'fixed';
    heartContainer.style.left = Math.random() * window.innerWidth + 'px';
    heartContainer.style.bottom = '0';
    heartContainer.style.pointerEvents = 'none';
    heartContainer.style.zIndex = '9999';
    document.body.appendChild(heartContainer);
    
    for (let i = 0; i < 5; i++) {
        const heart = document.createElement('div');
        heart.className = 'heart';
        heart.innerHTML = '❤';
        heart.style.position = 'absolute';
        heart.style.fontSize = Math.random() * 20 + 20 + 'px';
        heart.style.left = (Math.random() * 100 - 50) + 'px';
        heart.style.opacity = '0';
        heart.style.color = '#ff6b6b';
        heart.style.textShadow = '0 0 10px rgba(255, 107, 107, 0.8)';
        heartContainer.appendChild(heart);
        
        // Animate heart
        const animation = heart.animate([
            { opacity: 1, transform: 'translateY(0) scale(1)' },
            { opacity: 0, transform: `translateY(${-window.innerHeight - 100}px) scale(0)` }
        ], {
            duration: Math.random() * 3000 + 5000,
            easing: 'cubic-bezier(0.1, 0.8, 0.2, 1)'
        });
        
        animation.onfinish = () => heart.remove();
    }
    
    // Remove container after animation
    setTimeout(() => {
        heartContainer.remove();
    }, 6000);
}

// Create floating emojis effect
function createFloatingEmojis(x, y, emoji) {
    const emojiContainer = document.createElement('div');
    emojiContainer.className = 'emoji-container';
    emojiContainer.style.position = 'fixed';
    emojiContainer.style.left = x + 'px';
    emojiContainer.style.top = y + 'px';
    emojiContainer.style.pointerEvents = 'none';
    emojiContainer.style.zIndex = '9999';
    emojiContainer.style.fontSize = '30px';
    emojiContainer.innerHTML = emoji;
    document.body.appendChild(emojiContainer);
    
    // Animate emoji
    const animation = emojiContainer.animate([
        { opacity: 1, transform: 'translateY(0) scale(1) rotate(0deg)' },
        { opacity: 0, transform: `translateY(-100px) scale(1.5) rotate(360deg)` }
    ], {
        duration: 2000,
        easing: 'cubic-bezier(0.1, 0.8, 0.2, 1)'
    });
    
    animation.onfinish = () => emojiContainer.remove();
}

// Create confetti explosion
function createConfettiExplosion() {
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            createConfetti();
        }, i * 300);
    }
}

// Add touch support for mobile devices
document.addEventListener('touchmove', (e) => {
    // Prevent default scrolling on some elements for better mobile experience
    if (e.target.closest('.hero') || e.target.closest('.cake-container')) {
        // Allow default behavior
    }
    
    // Create sparkles on touch
    if (e.touches.length > 0) {
        createSparkles(e.touches[0].clientX, e.touches[0].clientY);
    }
});

document.addEventListener('touchstart', (e) => {
    if (e.touches.length > 0) {
        createHearts();
        
        // Add special effect to gallery items on touch
        if (e.target.closest('.gallery-item')) {
            const galleryItem = e.target.closest('.gallery-item');
            galleryItem.classList.add('animate');
            createSparkles(e.touches[0].clientX, e.touches[0].clientY);
            
            // Add temporary love effect
            setTimeout(() => {
                galleryItem.classList.remove('animate');
            }, 2000);
            
            // Prevent event from bubbling up
            e.stopPropagation();
        }
    }
});