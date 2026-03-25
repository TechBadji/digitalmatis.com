/* ══════════════════════════════════════════════
   DigitalMatis — Main JavaScript
══════════════════════════════════════════════ */

/* ─── Navbar scroll effect ──────────────────── */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}, { passive: true });


/* ─── Mobile menu burger ────────────────────── */
const burger      = document.getElementById('burger');
const mobileMenu  = document.getElementById('mobile-menu');

burger.addEventListener('click', () => {
  burger.classList.toggle('open');
  mobileMenu.classList.toggle('hidden');
});

// Close menu on link click
mobileMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    burger.classList.remove('open');
    mobileMenu.classList.add('hidden');
  });
});


/* ─── Scroll Reveal ─────────────────────────── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      // Optional: unobserve after reveal
      // revealObserver.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.12,
  rootMargin: '0px 0px -40px 0px'
});

document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right').forEach(el => {
  revealObserver.observe(el);
});


/* ─── Counter animation ─────────────────────── */
function animateCounter(el, target, duration = 1800) {
  let start = 0;
  const step = (timestamp) => {
    if (!start) start = timestamp;
    const progress = Math.min((timestamp - start) / duration, 1);
    // Ease out
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(ease * target);
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target + (el.dataset.suffix || '+');
  };
  requestAnimationFrame(step);
}

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      animateCounter(el, target);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.counter').forEach(el => {
  counterObserver.observe(el);
});


/* ─── Active nav link on scroll ─────────────── */
const sections = document.querySelectorAll('section[id]');
const navLinks  = document.querySelectorAll('.nav-link');

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const id = entry.target.getAttribute('id');
      navLinks.forEach(link => {
        link.style.color = link.getAttribute('href') === `#${id}`
          ? '#F47920'
          : '';
      });
    }
  });
}, { threshold: 0.5 });

sections.forEach(s => sectionObserver.observe(s));


/* ─── Contact form — EmailJS ────────────────── */
// ⚙️ CONFIGURATION : remplacer ces 2 valeurs depuis emailjs.com
const EMAILJS_SERVICE_ID  = 'service_mg6ktso';
const EMAILJS_TEMPLATE_ID = 'template_nzgjkvb';

const form = document.getElementById('contact-form');
if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn     = form.querySelector('button[type="submit"]');
    const original = btn.innerHTML;

    // État chargement
    btn.innerHTML  = '<span class="inline-flex items-center gap-2"><svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/></svg>Envoi en cours…</span>';
    btn.disabled   = true;
    btn.style.background = '#2A4A9A';

    try {
      await emailjs.sendForm(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, form);

      // Succès
      btn.innerHTML  = '✓ Message envoyé ! On vous répond sous 24h';
      btn.style.background = '#22C55E';

      setTimeout(() => {
        btn.innerHTML  = original;
        btn.style.background = '';
        btn.disabled   = false;
        form.reset();
      }, 4000);

    } catch (err) {
      // Erreur
      console.error('EmailJS error:', err);
      btn.innerHTML  = '✗ Erreur d\'envoi — réessayez';
      btn.style.background = '#EF4444';

      setTimeout(() => {
        btn.innerHTML  = original;
        btn.style.background = '';
        btn.disabled   = false;
      }, 3000);
    }
  });
}


/* ─── Smooth scroll for anchor links ────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80; // navbar height
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});
