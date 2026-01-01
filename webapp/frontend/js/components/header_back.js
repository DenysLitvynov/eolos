// frontend/js/components/header_back.js

async function loadHeaderBack() {
  const mount = document.getElementById("site-header");
  if (!mount) return;

  // Cargar el HTML del header-back
  const res = await fetch("/header_back.html", { cache: "no-cache" });
  if (!res.ok) {
    console.error("No se pudo cargar header_back.html:", res.status);
    return;
  }

  mount.innerHTML = await res.text();

  /* ===============================
     LÓGICA BOTÓN "VOLVER ATRÁS"
     =============================== */
  const backBtn = mount.querySelector('[data-action="back"]');

  if (backBtn) {
    backBtn.addEventListener("click", () => {
      // Si hay historial, volver atrás; si no, ir al inicio
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = "/index.html";
      }
    });
  }

  /* ===============================
     LÓGICA MENÚ (por coherencia)
     =============================== */
  const header = mount.querySelector(".header");
  const nav = header?.querySelector(".nav");
  const toggleBtn = header?.querySelector(".menu-toggle");

  if (!header || !nav || !toggleBtn) return;

  function closeMenu() {
    toggleBtn.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  }

  function openMenu() {
    toggleBtn.setAttribute("aria-expanded", "true");
    nav.classList.add("is-open");
  }

  toggleBtn.addEventListener("click", () => {
    const expanded = toggleBtn.getAttribute("aria-expanded") === "true";
    expanded ? closeMenu() : openMenu();
  });

  window.addEventListener("resize", () => {
    const bp = Number(header.dataset.breakpoint || 1050);
    if (window.innerWidth > bp) closeMenu();
  });
}

// Ejecutar
loadHeaderBack();
