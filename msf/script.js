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

// Simple direct load — background.jpeg is always same-origin (file:// or localhost),
// so no CORS issue and canvas will NOT be tainted.
officialPosterImg.onload = function () {
    officialPosterLoaded = true;
    if (typeof refreshPosterGlobal === 'function') refreshPosterGlobal();
};
officialPosterImg.onerror = function () {
    console.error('background.jpeg load failed — check assets/ folder');
};
officialPosterImg.src = 'assets/background.jpeg';


function drawRoundedRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
}

function drawPoster(userImg, nameText) {
    const canvas = document.getElementById('posterCanvas');
    if (!canvas || !officialPosterLoaded) return;
    const ctx = canvas.getContext('2d');

    // background.jpeg is square (1080x1080). Lock canvas to 1080x1080.
    const SIZE = 1080;
    canvas.width  = SIZE;
    canvas.height = SIZE;
    ctx.clearRect(0, 0, SIZE, SIZE);

    // 1. Draw background.jpeg scaled to fill the square canvas
    const bw = officialPosterImg.width  || SIZE;
    const bh = officialPosterImg.height || SIZE;
    const bScale = Math.max(SIZE / bw, SIZE / bh);
    const bDrawW = bw * bScale;
    const bDrawH = bh * bScale;
    ctx.drawImage(officialPosterImg,
        (SIZE - bDrawW) / 2, (SIZE - bDrawH) / 2,
        bDrawW, bDrawH);

    // ── Layout constants ──────────────────────────────────────────────────────
    // The background has:
    //   top band  : ~0 – 230px  (logo + title + date)
    //   empty zone: ~230 – 770px  ← we place content here
    //   bottom band: ~770 – 1080px (event info)
    const ZONE_TOP    = 250;   // top of the empty center zone
    const ZONE_BOTTOM = 760;   // bottom of the empty center zone
    const ZONE_MID_Y  = (ZONE_TOP + ZONE_BOTTOM) / 2;  // ≈ 505

    const LEFT_CX  = SIZE * 0.27;   // photo circle center-x  (left third)
    const RIGHT_CX = SIZE * 0.68;   // text block center-x    (right portion)

    // ── Photo radius ─────────────────────────────────────────────────────────
    const R = 155;   // radius in px
    const photocy = ZONE_MID_Y + 10;

    // ── 2. Draw outer glow ring ───────────────────────────────────────────────
    const gradient = ctx.createRadialGradient(
        LEFT_CX, photocy, R + 4,
        LEFT_CX, photocy, R + 22
    );
    gradient.addColorStop(0,   'rgba(21,122,70,0.55)');
    gradient.addColorStop(0.5, 'rgba(21,122,70,0.20)');
    gradient.addColorStop(1,   'rgba(21,122,70,0.00)');
    ctx.beginPath();
    ctx.arc(LEFT_CX, photocy, R + 22, 0, Math.PI * 2);
    ctx.fillStyle = gradient;
    ctx.fill();

    // ── 3. Clip & draw user photo ─────────────────────────────────────────────
    if (userImg) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(LEFT_CX, photocy, R, 0, Math.PI * 2);
        ctx.closePath();
        ctx.clip();

        const ir = userImg.width / userImg.height;
        let dw, dh, dx, dy;
        if (ir > 1) {
            dh = R * 2;  dw = dh * ir;
            dx = LEFT_CX - dw / 2;  dy = photocy - R;
        } else {
            dw = R * 2;  dh = dw / ir;
            dx = LEFT_CX - R;  dy = photocy - dh / 2;
        }
        ctx.drawImage(userImg, dx, dy, dw, dh);
        ctx.restore();
    } else {
        // placeholder silhouette
        ctx.save();
        ctx.beginPath();
        ctx.arc(LEFT_CX, photocy, R, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(200,230,210,0.60)';
        ctx.fill();
        ctx.restore();
    }

    // ── 4. Green border ring ──────────────────────────────────────────────────
    ctx.strokeStyle = '#157a46';
    ctx.lineWidth   = 6;
    ctx.beginPath();
    ctx.arc(LEFT_CX, photocy, R + 4, 0, Math.PI * 2);
    ctx.stroke();

    // thin white inner ring
    ctx.strokeStyle = 'rgba(255,255,255,0.7)';
    ctx.lineWidth   = 2.5;
    ctx.beginPath();
    ctx.arc(LEFT_CX, photocy, R - 3, 0, Math.PI * 2);
    ctx.stroke();

    // ── 5. Name badge below photo ─────────────────────────────────────────────
    if (nameText) {
        const badgeFontSize = 26;
        ctx.font = `700 ${badgeFontSize}px "Outfit", sans-serif`;
        const tw = ctx.measureText(nameText).width;
        const bW  = tw + 36;
        const bH  = 40;
        const bX  = LEFT_CX - bW / 2;
        const bY  = photocy + R + 16;

        // shadow
        ctx.shadowColor = 'rgba(0,0,0,0.18)';
        ctx.shadowBlur  = 8;

        drawRoundedRect(ctx, bX, bY, bW, bH, 10);
        ctx.fillStyle = '#157a46';
        ctx.fill();

        ctx.shadowBlur = 0;
        ctx.fillStyle  = '#ffffff';
        ctx.textAlign  = 'center';
        ctx.fillText(nameText, LEFT_CX, bY + bH - 10);
    }

    // ── 6. Right-side text: "ഞാനും" + "പങ്കെടുക്കുന്നു" ───────────────────────
    const textBlockCenterY = ZONE_MID_Y;

    // decorative top dash line
    ctx.strokeStyle = '#157a46';
    ctx.lineWidth   = 3;
    ctx.setLineDash([10, 6]);
    const lineLeft  = RIGHT_CX - 140;
    const lineRight = RIGHT_CX + 140;
    ctx.beginPath();
    ctx.moveTo(lineLeft,  textBlockCenterY - 118);
    ctx.lineTo(lineRight, textBlockCenterY - 118);
    ctx.stroke();
    ctx.setLineDash([]);

    // "ഞാനും"
    ctx.shadowColor = 'rgba(0,0,0,0.10)';
    ctx.shadowBlur  = 6;
    ctx.fillStyle   = '#104e2d';
    ctx.font        = `bold 72px "Noto Serif Malayalam", "Chilanka", serif`;
    ctx.textAlign   = 'center';
    ctx.fillText('ഞാനും', RIGHT_CX, textBlockCenterY - 48);

    // "പങ്കെടുക്കുന്നു"
    ctx.font      = `900 58px "Noto Serif Malayalam", "Chilanka", serif`;
    ctx.fillStyle = '#157a46';
    ctx.fillText('പങ്കെടുക്കുന്നു', RIGHT_CX, textBlockCenterY + 24);

    // decorative bottom dash line
    ctx.strokeStyle = '#157a46';
    ctx.lineWidth   = 3;
    ctx.setLineDash([10, 6]);
    ctx.beginPath();
    ctx.moveTo(lineLeft,  textBlockCenterY + 54);
    ctx.lineTo(lineRight, textBlockCenterY + 54);
    ctx.stroke();
    ctx.setLineDash([]);

    // small green dot accent
    ctx.shadowBlur = 0;
    [RIGHT_CX - 30, RIGHT_CX, RIGHT_CX + 30].forEach(dotX => {
        ctx.beginPath();
        ctx.arc(dotX, textBlockCenterY + 78, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#157a46';
        ctx.fill();
    });

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
    
    // Expose refreshPoster globally so the background image load callback can call it
    window.refreshPosterGlobal = refreshPoster;

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
