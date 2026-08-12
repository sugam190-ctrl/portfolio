const header = document.querySelector(".site-header");
const nav = document.querySelector("#nav");
const menuBtn = document.querySelector(".menu-btn");
const cursorGlow = document.querySelector(".cursor-glow");
const toast = document.querySelector("#toast");

// Mobile navigation
menuBtn?.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("open");
  menuBtn.setAttribute("aria-expanded", String(isOpen));
});

document.querySelectorAll(".nav a").forEach(link => {
  link.addEventListener("click", () => {
    nav.classList.remove("open");
    menuBtn?.setAttribute("aria-expanded", "false");
  });
});

// Header changes when scrolling
const updateHeader = () => {
  if (header) {
    header.classList.toggle("scrolled", window.scrollY > 30);
  }
};

window.addEventListener("scroll", updateHeader, { passive: true });
updateHeader();

// Reveal elements when they enter the screen
const revealItems = document.querySelectorAll(".reveal");

const revealObserver = new IntersectionObserver(
  entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  {
    threshold: 0.12
  }
);

revealItems.forEach(item => {
  revealObserver.observe(item);
});

// Cursor glow on desktop
if (window.matchMedia("(pointer:fine)").matches && cursorGlow) {
  window.addEventListener("mousemove", event => {
    cursorGlow.style.left = `${event.clientX}px`;
    cursorGlow.style.top = `${event.clientY}px`;
    cursorGlow.style.opacity = "1";
  });

  document.addEventListener("mouseleave", () => {
    cursorGlow.style.opacity = "0";
  });
}

// Project buttons
document.querySelectorAll("[data-demo]").forEach(link => {
  link.addEventListener("click", event => {
    event.preventDefault();

    const projectName = link.dataset.demo;

    showToast(
      `${projectName} — add your live project URL here`
    );
  });
});

// Toast notification
function showToast(message) {
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("show");

  clearTimeout(window.__toastTimer);

  window.__toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2600);
}

// Project card 3D hover effect
if (window.matchMedia("(pointer:fine)").matches) {
  document.querySelectorAll(".project").forEach(card => {

    card.addEventListener("mousemove", event => {
      const rect = card.getBoundingClientRect();

      const x =
        (event.clientX - rect.left) /
        rect.width -
        0.5;

      const y =
        (event.clientY - rect.top) /
        rect.height -
        0.5;

      card.style.transform =
        `perspective(1000px)
         rotateX(${y * -1.5}deg)
         rotateY(${x * 1.5}deg)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "";
    });

  });
}
