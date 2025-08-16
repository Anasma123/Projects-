document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle with improved animation
    const menuToggle = document.getElementById('menuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    const closeMenu = document.getElementById('closeMenu');
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    
    menuToggle.addEventListener('click', () => {
        mobileMenu.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        
        gsap.to(mobileMenu, {
            opacity: 1,
            duration: 0.3,
            ease: "power2.out"
        });
        
        gsap.to(mobileLinks, {
            y: 0,
            opacity: 1,
            stagger: 0.1,
            duration: 0.5,
            delay: 0.2,
            ease: "power2.out"
        });
    });
    
    closeMenu.addEventListener('click', () => {
        gsap.to(mobileLinks, {
            y: 20,
            opacity: 0,
            stagger: 0.05,
            duration: 0.3,
            ease: "power2.in"
        });
        
        gsap.to(mobileMenu, {
            opacity: 0,
            duration: 0.3,
            delay: 0.2,
            ease: "power2.out",
            onComplete: () => {
                mobileMenu.classList.add('hidden');
                document.body.style.overflow = '';
            }
        });
    });

    // Dark Mode Toggle with localStorage support
    const darkModeToggle = document.getElementById('darkModeToggle');
    
    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark');
    } else if (localStorage.getItem('darkMode') === null && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.body.classList.add('dark');
        localStorage.setItem('darkMode', 'true');
    }
    
    darkModeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const isDark = document.body.classList.contains('dark');
        localStorage.setItem('darkMode', isDark);
        
        // Animate the toggle
        gsap.fromTo(darkModeToggle, 
            { scale: 0.8 },
            { 
                scale: 1.2,
                duration: 0.3,
                yoyo: true,
                repeat: 1,
                ease: "power2.out"
            }
        );
    });

    // Smooth Scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                gsap.to(window, {
                    duration: 1,
                    scrollTo: {
                        y: target,
                        offsetY: 80
                    },
                    ease: "power2.inOut"
                });
                
                // Close mobile menu if open
                if (!mobileMenu.classList.contains('hidden')) {
                    gsap.to(mobileLinks, {
                        y: 20,
                        opacity: 0,
                        stagger: 0.05,
                        duration: 0.3,
                        ease: "power2.in"
                    });
                    
                    gsap.to(mobileMenu, {
                        opacity: 0,
                        duration: 0.3,
                        delay: 0.2,
                        ease: "power2.out",
                        onComplete: () => {
                            mobileMenu.classList.add('hidden');
                            document.body.style.overflow = '';
                        }
                    });
                }
            }
        });
    });

    // GSAP Animations
    gsap.registerPlugin(ScrollTrigger);

    // Welcome popup animation
    gsap.from('#welcome-popup .popup', {
        scale: 0.8,
        opacity: 0,
        duration: 0.8,
        ease: "back.out(1.7)",
        delay: 0.5
    });

    // Section title animations
    gsap.utils.toArray('.section-title, .section-title-light').forEach(title => {
        gsap.from(title, {
            scrollTrigger: {
                trigger: title,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            y: 30,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out"
        });
        
        gsap.from(title.querySelector('::after'), {
            scrollTrigger: {
                trigger: title,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            scaleX: 0,
            duration: 0.8,
            ease: "power3.out",
            delay: 0.3
        });
    });

    // Feature cards animation
    gsap.utils.toArray('.feature-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            y: 50,
            opacity: 0,
            duration: 0.6,
            ease: "power2.out",
            delay: i * 0.1
        });
    });

    // Leader cards animation - single row in mobile
    gsap.utils.toArray('.leader-card').forEach(card => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            y: 100,
            opacity: 0,
            duration: 0.8,
            ease: "power3.out"
        });
    });

    // Staff cards animation - 2 per row in mobile
    gsap.utils.toArray('.staff-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            y: 50,
            opacity: 0,
            duration: 0.5,
            ease: "power2.out",
            delay: i * 0.1
        });
    });

    // Gallery slider animation
    const gallerySlides = document.querySelectorAll('.gallery-slide');
    gallerySlides.forEach((slide, i) => {
        gsap.from(slide, {
            scrollTrigger: {
                trigger: slide,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            x: i % 2 === 0 ? -50 : 50,
            opacity: 0,
            duration: 0.6,
            ease: "power2.out",
            delay: i * 0.1
        });
    });

    // Gallery image popup functionality
    gallerySlides.forEach(slide => {
        slide.addEventListener('click', function() {
            const imgSrc = this.querySelector('img').src;
            const caption = this.querySelector('h3').textContent + ' - ' + this.querySelector('p').textContent;
            
            document.getElementById('popup-image').src = imgSrc;
            document.getElementById('popup-caption').textContent = caption;
            
            const popup = document.getElementById('image-popup');
            popup.__x.$data.open = true;
            
            // Animate popup
            gsap.fromTo(popup, 
                { opacity: 0 },
                { opacity: 1, duration: 0.3 }
            );
            gsap.fromTo('#popup-image', 
                { scale: 0.8, opacity: 0 },
                { scale: 1, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }
            );
        });
    });

    // Success cards animation
    gsap.utils.toArray('.success-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: "top 80%",
                toggleActions: "play none none none"
            },
            y: 50,
            opacity: 0,
            duration: 0.5,
            ease: "power2.out",
            delay: i * 0.1
        });
    });

    // Staff popups animation
    document.querySelectorAll('[id^="staff-popup-"]').forEach(popup => {
        gsap.from(popup.querySelector('.popup'), {
            scale: 0.8,
            opacity: 0,
            duration: 0.5,
            ease: "back.out(1.7)"
        });
    });

    // Gallery navigation arrows
    const galleryTrack = document.querySelector('.gallery-track');
    const galleryPrev = document.querySelector('.gallery-prev');
    const galleryNext = document.querySelector('.gallery-next');
    
    if (galleryTrack && galleryPrev && galleryNext) {
        galleryPrev.addEventListener('click', () => {
            gsap.to(galleryTrack, {
                scrollLeft: galleryTrack.scrollLeft - 300,
                duration: 0.5,
                ease: "power2.out"
            });
        });
        
        galleryNext.addEventListener('click', () => {
            gsap.to(galleryTrack, {
                scrollLeft: galleryTrack.scrollLeft + 300,
                duration: 0.5,
                ease: "power2.out"
            });
        });
    }

    // Animate elements when they come into view
    const animateOnScroll = (elements, animation) => {
        elements.forEach(element => {
            if (!element) return;
            
            gsap.from(element, {
                scrollTrigger: {
                    trigger: element,
                    start: "top 80%",
                    toggleActions: "play none none none"
                },
                ...animation
            });
        });
    };

    // Animate all cards
    animateOnScroll(document.querySelectorAll('.animate-card'), {
        y: 30,
        opacity: 0,
        duration: 0.8,
        stagger: 0.1,
        ease: "power2.out"
    });
});