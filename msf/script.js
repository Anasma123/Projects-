// Urava 2026 Event Registration Portal JavaScript
// Designed & Developed for MSF Poovattuparamba Town Unit Committee

const targetEventDate = new Date('June 20, 2026 00:00:00');
const registrationDeadline = new Date('June 16, 2026 23:59:59');

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.16 });

    document.querySelectorAll('.reveal').forEach(el => {
        observer.observe(el);
    });
}

function initButtonRipples() {
    document.querySelectorAll('.btn-primary, .btn-secondary').forEach(button => {
        button.addEventListener('pointerdown', function (event) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height) * 1.2;
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${event.clientY - rect.top - size / 2}px`;
            button.appendChild(ripple);
            setTimeout(() => ripple.remove(), 700);
        });
    });
}

function addPulse(element) {
    if (!element) return;
    element.classList.add('pulse');
    setTimeout(() => element.classList.remove('pulse'), 450);
}

function initCountdown() {
    const daysEl = document.getElementById('eventDays');
    const hoursEl = document.getElementById('eventHours');
    const minutesEl = document.getElementById('eventMinutes');
    const secondsEl = document.getElementById('eventSeconds');

    function updateTimer() {
        const now = new Date();
        const difference = targetEventDate.getTime() - now.getTime();

        if (difference <= 0) {
            if (daysEl) daysEl.textContent = '00';
            if (hoursEl) hoursEl.textContent = '00';
            if (minutesEl) minutesEl.textContent = '00';
            if (secondsEl) secondsEl.textContent = '00';
            return;
        }

        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((difference / (1000 * 60)) % 60);
        const seconds = Math.floor((difference / 1000) % 60);

        if (daysEl) {
            daysEl.textContent = String(days).padStart(2, '0');
            addPulse(daysEl);
        }
        if (hoursEl) {
            hoursEl.textContent = String(hours).padStart(2, '0');
            addPulse(hoursEl);
        }
        if (minutesEl) {
            minutesEl.textContent = String(minutes).padStart(2, '0');
            addPulse(minutesEl);
        }
        if (secondsEl) {
            secondsEl.textContent = String(seconds).padStart(2, '0');
            addPulse(secondsEl);
        }
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}

function initRegistrationCountdown() {
    const dEl = document.getElementById('regDays');
    const hEl = document.getElementById('regHours');
    const mEl = document.getElementById('regMinutes');
    const sEl = document.getElementById('regSeconds');
    const registerBtn = document.getElementById('registerBtn');
    const externalRegisterBtn = document.getElementById('externalRegisterBtn');
    const deadlineContainer = document.getElementById('regCountdownContainer');

    function updateRegTimer() {
        const now = new Date();
        const diff = registrationDeadline.getTime() - now.getTime();

        if (diff <= 0) {
            if (deadlineContainer) {
                deadlineContainer.innerHTML = '<div class="deadline-closed">രജിസ്ട്രേഷൻ അവസാനിച്ചു</div>';
            }
            if (registerBtn) registerBtn.disabled = true;
            if (externalRegisterBtn) {
                externalRegisterBtn.disabled = true;
                externalRegisterBtn.textContent = 'Registration Closed';
            }
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((diff / (1000 * 60)) % 60);
        const seconds = Math.floor((diff / 1000) % 60);

        if (dEl) {
            dEl.textContent = String(days).padStart(2, '0');
            addPulse(dEl);
        }
        if (hEl) {
            hEl.textContent = String(hours).padStart(2, '0');
            addPulse(hEl);
        }
        if (mEl) {
            mEl.textContent = String(minutes).padStart(2, '0');
            addPulse(mEl);
        }
        if (sEl) {
            sEl.textContent = String(seconds).padStart(2, '0');
            addPulse(sEl);
        }
    }

    updateRegTimer();
    setInterval(updateRegTimer, 1000);
}

function scrollToSection(id) {
    const element = document.getElementById(id);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function initRegistration() {
    const externalRegisterBtn = document.getElementById('externalRegisterBtn');
    if (externalRegisterBtn) {
        externalRegisterBtn.addEventListener('click', function () {
            window.open(
                "https://form.svhrt.com/6a1ed66f232308702926e476",
                "_blank"
            );
        });
    }
}

function initGallery() {
    const grid = document.getElementById('galleryGrid');
    if (!grid) return;
    const total = 14;
    for (let i = 1; i <= total; i += 1) {
        const card = document.createElement('div');
        card.className = 'gallery-card glass-card';
        const img = document.createElement('img');
        img.alt = `Program ${i}`;
        img.loading = 'lazy';
        img.src = `assets/p${i}.jpeg`;
        img.onerror = function () { this.src = `assets/p${i}.jpg`; };
        card.appendChild(img);
        card.addEventListener('click', function () {
            openLightbox(img.src);
        });
        grid.appendChild(card);
    }
}

function openLightbox(src) {
    const lb = document.getElementById('lightbox');
    const lbImg = document.getElementById('lightboxImg');
    if (!lb || !lbImg) return;
    lbImg.src = src;
    lb.classList.add('show');
}

function closeLightbox() {
    const lb = document.getElementById('lightbox');
    if (!lb) return;
    lb.classList.remove('show');
}

document.addEventListener('click', function (e) {
    const lb = document.getElementById('lightbox');
    if (!lb) return;
    if (e.target === lb || e.target.id === 'lightboxImg') {
        closeLightbox();
    }
});

document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeLightbox();
});

let currentUploadedImage = null;
let officialPosterLoaded = false;
const officialPosterImg = new Image();
officialPosterImg.src = 'assets/official-poster.jpeg';
officialPosterImg.onload = function() {
    officialPosterLoaded = true;
};

function drawPoster(userImg, nameText) {
    const canvas = document.getElementById('posterCanvas');
    if (!canvas || !officialPosterLoaded) return;
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions dynamically to match the official poster
    canvas.width = officialPosterImg.width;
    canvas.height = officialPosterImg.height;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 1. Draw the base official poster background
    ctx.drawImage(officialPosterImg, 0, 0, canvas.width, canvas.height);
    
    // 2. Calculate coordinates dynamically based on canvas dimensions (e.g. 750x1060 base)
    const baseW = 750;
    const baseH = 1060;
    const scale = canvas.width / baseW;
    
    // 3. User photo circular frame in the bottom-left wave area (positioned below Y: 800 to avoid text overlap)
    const cx = 105 * scale;
    const cy = 900 * scale;
    const r = 58 * scale;
    
    if (userImg) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.closePath();
        ctx.clip();
        
        const imgWidth = userImg.width;
        const imgHeight = userImg.height;
        const imgRatio = imgWidth / imgHeight;
        
        let drawWidth, drawHeight, drawX, drawY;
        if (imgRatio > 1) {
            drawHeight = r * 2;
            drawWidth = drawHeight * imgRatio;
            drawX = cx - drawWidth / 2;
            drawY = cy - r;
        } else {
            drawWidth = r * 2;
            drawHeight = drawWidth / imgRatio;
            drawX = cx - r;
            drawY = cy - drawHeight / 2;
        }
        
        ctx.drawImage(userImg, drawX, drawY, drawWidth, drawHeight);
        ctx.restore();
        
        // Green Ring matching the theme
        ctx.strokeStyle = '#157a46';
        ctx.lineWidth = 3 * scale;
        ctx.beginPath();
        ctx.arc(cx, cy, r + 1.5 * scale, 0, Math.PI * 2);
        ctx.stroke();
    }
    
    // 4. Draw name banner below the photo
    if (nameText) {
        ctx.font = `800 ${Math.round(15 * scale)}px "Outfit", "Noto Serif Malayalam", sans-serif`;
        ctx.textAlign = 'center';
        
        const textWidth = ctx.measureText(nameText).width;
        const bannerW = Math.max(90 * scale, textWidth + 18 * scale);
        const bannerH = 26 * scale;
        const bannerX = cx - bannerW / 2;
        const bannerY = (cy + r + 10 * scale);
        
        ctx.fillStyle = '#157a46'; // Forest green theme color
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1 * scale;
        
        // Rounded corner banner
        const rx = bannerX;
        const ry = bannerY;
        const rw = bannerW;
        const rh = bannerH;
        const rad = 5 * scale;
        
        ctx.beginPath();
        ctx.moveTo(rx + rad, ry);
        ctx.lineTo(rx + rw - rad, ry);
        ctx.quadraticCurveTo(rx + rw, ry, rx + rw, ry + rad);
        ctx.lineTo(rx + rw, ry + rh - rad);
        ctx.quadraticCurveTo(rx + rw, ry + rh, rx + rw - rad, ry + rh);
        ctx.lineTo(rx + rad, ry + rh);
        ctx.quadraticCurveTo(rx, ry + rh, rx, ry + rh - rad);
        ctx.lineTo(rx, ry + rad);
        ctx.quadraticCurveTo(rx, ry, rx + rad, ry);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Name Text inside badge
        ctx.fillStyle = '#ffffff';
        ctx.fillText(nameText, cx, bannerY + 18 * scale);
    }
    
    // 5. Draw "ഞാനും പങ്കെടുക്കുന്നു!" above the photo
    ctx.shadowColor = 'rgba(255, 255, 255, 0.9)';
    ctx.shadowBlur = 6 * scale;
    ctx.fillStyle = '#104e2d'; // Deep green
    ctx.font = `bold ${Math.round(20 * scale)}px "Chilanka", "Gayathri", cursive`;
    ctx.fillText('ഞാനും', cx, cy - r - 26 * scale);
    ctx.fillText('പങ്കെടുക്കുന്നു!', cx, cy - r - 6 * scale);
    
    // Reset shadow
    ctx.shadowBlur = 0;
}

function initPosterGenerator() {
    const userPhotoInput = document.getElementById('userPhoto');
    const userNameInput = document.getElementById('userName');
    const downloadPosterBtn = document.getElementById('downloadPosterBtn');
    const photoLabel = document.getElementById('photoLabel');
    const previewPlaceholder = document.getElementById('previewPlaceholder');
    const canvas = document.getElementById('posterCanvas');

    if (!userPhotoInput || !userNameInput || !downloadPosterBtn) return;

    function refreshPoster() {
        if (currentUploadedImage && officialPosterLoaded) {
            if (previewPlaceholder) previewPlaceholder.style.display = 'none';
            if (canvas) canvas.style.display = 'block';
            drawPoster(currentUploadedImage, userNameInput.value.trim());
            downloadPosterBtn.disabled = false;
        } else {
            if (previewPlaceholder) previewPlaceholder.style.display = 'flex';
            if (canvas) canvas.style.display = 'none';
            downloadPosterBtn.disabled = true;
        }
    }

    userPhotoInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (!file) {
            currentUploadedImage = null;
            if (photoLabel) photoLabel.textContent = 'ഫോട്ടോ തിരഞ്ഞെടുക്കുക';
            refreshPoster();
            return;
        }
        
        if (photoLabel) photoLabel.textContent = file.name;

        const reader = new FileReader();
        reader.onload = function (e) {
            const img = new Image();
            img.onload = function () {
                currentUploadedImage = img;
                refreshPoster();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });

    userNameInput.addEventListener('input', function () {
        refreshPoster();
    });

    downloadPosterBtn.addEventListener('click', function () {
        if (!canvas) return;
        const link = document.createElement('a');
        link.download = 'urava-campaign-poster.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    });
    
    // If the background image loads after the user has selected their picture
    officialPosterImg.addEventListener('load', function() {
        refreshPoster();
    });
}

window.addEventListener('DOMContentLoaded', function () {
    initCountdown();
    initRegistration();
    initRegistrationCountdown();
    initGallery();
    initScrollAnimations();
    initButtonRipples();
    initPosterGenerator();
});
