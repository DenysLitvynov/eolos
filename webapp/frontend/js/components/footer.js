async function loadFooter() {
  const container = document.getElementById('site-footer');
  if (!container) return;

  try {
    const res = await fetch('/footer.html');
    if (!res.ok) throw new Error('No se pudo cargar footer.html');

    const html = await res.text();
    container.innerHTML = html;
  } catch (e) {
    console.error("[FOOTER] Error cargando footer:", e);
  }
}

document.addEventListener("DOMContentLoaded", loadFooter);