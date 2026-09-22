// =================== NAVBAR ===================
const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');

window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
});

navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => navLinks.classList.remove('active'));
});

// =================== COUNTER ANIMATION ===================
function animateCounters() {
    document.querySelectorAll('.stat-num').forEach(el => {
        const target = parseInt(el.dataset.target);
        let current = 0;
        const step = target / 40;
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                el.textContent = target;
                clearInterval(timer);
            } else {
                el.textContent = Math.floor(current);
            }
        }, 30);
    });
}

const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            heroObserver.disconnect();
        }
    });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) heroObserver.observe(heroStats);

// =================== EXERCISE FILTERS ===================
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;
        document.querySelectorAll('.exercise-card').forEach(card => {
            if (filter === 'all' || card.dataset.category === filter) {
                card.style.display = '';
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'all 0.4s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 50);
            } else {
                card.style.display = 'none';
            }
        });
    });
});

// =================== SCROLL ANIMATIONS ===================
const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .benefit-card, .tip-card, .exercise-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    scrollObserver.observe(el);
});

// =================== TEMPORIZADOR GENERAL ===================
let timerInterval = null;
let timerSeconds = 180;
let timerTotal = 180;
let timerRunning = false;
const circumference = 2 * Math.PI * 90;

function formatTime(seconds) {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
}

function updateTimerDisplay() {
    document.getElementById('timerDisplay').textContent = formatTime(timerSeconds);
    const progress = document.getElementById('timerProgress');
    const offset = circumference * (1 - timerSeconds / timerTotal);
    progress.style.strokeDashoffset = offset;
}

document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (timerRunning) return;
        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        timerTotal = parseInt(btn.dataset.time);
        timerSeconds = timerTotal;
        updateTimerDisplay();
        document.getElementById('timerStatus').textContent = 'Listo';
        document.getElementById('timerInstruction').textContent = 'Selecciona un tiempo y presiona Iniciar para comenzar tu pausa activa';
    });
});

function toggleTimer() {
    const btn = document.getElementById('btnStartTimer');
    if (timerRunning) {
        clearInterval(timerInterval);
        timerRunning = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Continuar';
        document.getElementById('timerStatus').textContent = 'Pausado';
    } else {
        timerRunning = true;
        btn.innerHTML = '<i class="fas fa-pause"></i> Pausar';
        document.getElementById('timerStatus').textContent = 'En progreso';
        document.getElementById('timerInstruction').textContent = 'Relájate, respira profundo y sigue moviéndote. ¡Tu cuerpo te lo agradecerá!';

        timerInterval = setInterval(() => {
            timerSeconds--;
            updateTimerDisplay();
            if (timerSeconds <= 0) {
                clearInterval(timerInterval);
                timerRunning = false;
                btn.innerHTML = '<i class="fas fa-play"></i> Iniciar';
                document.getElementById('timerStatus').textContent = '¡Completado!';
                document.getElementById('timerInstruction').textContent = '¡Excelente! Has completado tu pausa activa. Siéntete mejor y continúa con tu día.';
                playNotification();
            }
        }, 1000);
    }
}

function resetTimer() {
    clearInterval(timerInterval);
    timerRunning = false;
    timerSeconds = timerTotal;
    updateTimerDisplay();
    document.getElementById('btnStartTimer').innerHTML = '<i class="fas fa-play"></i> Iniciar';
    document.getElementById('timerStatus').textContent = 'Listo';
    document.getElementById('timerInstruction').textContent = 'Selecciona un tiempo y presiona Iniciar para comenzar tu pausa activa';
}

// =================== EJERCICIO MODAL ===================
let exerciseInterval = null;
let exerciseSeconds = 0;
let exerciseTotal = 0;
let exerciseRunning = false;
const exerciseCircumference = 2 * Math.PI * 90;

function startExercise(btn, seconds, title, instruction) {
    exerciseTotal = seconds;
    exerciseSeconds = seconds;

    document.getElementById('exerciseModalTitle').textContent = title;
    document.getElementById('exerciseInstruction').textContent = instruction;
    document.getElementById('exerciseTime').textContent = formatTime(seconds);
    document.getElementById('exerciseStatus').textContent = 'En progreso';
    document.getElementById('exerciseProgress').style.strokeDashoffset = 0;

    const modal = document.getElementById('exerciseModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    exerciseRunning = true;
    document.getElementById('btnExercisePause').innerHTML = '<i class="fas fa-pause"></i> Pausar';

    exerciseInterval = setInterval(() => {
        exerciseSeconds--;
        document.getElementById('exerciseTime').textContent = formatTime(exerciseSeconds);
        const offset = exerciseCircumference * (1 - exerciseSeconds / exerciseTotal);
        document.getElementById('exerciseProgress').style.strokeDashoffset = offset;

        if (exerciseSeconds <= 0) {
            clearInterval(exerciseInterval);
            exerciseRunning = false;
            document.getElementById('exerciseStatus').textContent = '¡Completado!';
            document.getElementById('btnExercisePause').style.display = 'none';
            playNotification();
        }
    }, 1000);
}

function pauseExercise() {
    const btn = document.getElementById('btnExercisePause');
    if (exerciseRunning) {
        clearInterval(exerciseInterval);
        exerciseRunning = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Continuar';
        document.getElementById('exerciseStatus').textContent = 'Pausado';
    } else {
        exerciseRunning = true;
        btn.innerHTML = '<i class="fas fa-pause"></i> Pausar';
        document.getElementById('exerciseStatus').textContent = 'En progreso';
        exerciseInterval = setInterval(() => {
            exerciseSeconds--;
            document.getElementById('exerciseTime').textContent = formatTime(exerciseSeconds);
            const offset = exerciseCircumference * (1 - exerciseSeconds / exerciseTotal);
            document.getElementById('exerciseProgress').style.strokeDashoffset = offset;
            if (exerciseSeconds <= 0) {
                clearInterval(exerciseInterval);
                exerciseRunning = false;
                document.getElementById('exerciseStatus').textContent = '¡Completado!';
                btn.style.display = 'none';
                playNotification();
            }
        }, 1000);
    }
}

function stopExercise() {
    clearInterval(exerciseInterval);
    exerciseRunning = false;
    closeExerciseModal();
}

function closeExerciseModal() {
    document.getElementById('exerciseModal').classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('btnExercisePause').style.display = '';
}

// =================== NOTIFICATION SOUND ===================
function playNotification() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        [523.25, 659.25, 783.99].forEach((freq, i) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = freq;
            osc.type = 'sine';
            gain.gain.setValueAtTime(0.3, ctx.currentTime + i * 0.15);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.15 + 0.5);
            osc.start(ctx.currentTime + i * 0.15);
            osc.stop(ctx.currentTime + i * 0.15 + 0.5);
        });
    } catch (e) { }
}

// =================== SMOOTH SCROLL ===================
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(a.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// =================== INIT ===================
updateTimerDisplay();
