import {
  getMainRole,
  isLoggedIn,
  logoutAndRedirect,
  getToken,
} from '../utilidades/auth.js';

// Menús según rol
const NAV_CONFIG = {
  guest: [
    { label: 'Inicio', href: '/index.html' },
    { label: 'Mapas', href: '/pages/mapas.html' },
    { label: 'Sobre nosotros', href: '/pages/sobre-nosotros.html' },
    { label: 'FAQ', href: '/pages/FAQ.html' },
    { label: 'Contacto', href: '/pages/contacto.html' },
    { label: 'Inicia Sesión', href: '/pages/login.html', className: 'login' },
    { label: 'Registrarse', href: '/pages/registro.html', className: 'registro' },
  ],

  usuario: [
    { label: 'Inicio', href: '/pages/landing-registrado.html' },
    { label: 'Mapas', href: '/pages/mapas.html' },
    { label: 'Sobre nosotros', href: '/pages/sobre-nosotros.html' },
    { label: 'FAQ', href: '/pages/FAQ.html' },
    { label: 'Recompensas', href: '/pages/recompensas.html' },
    { label: 'Contacto', href: '/pages/contacto.html' },
    { label: 'Perfil', href: '/pages/perfil.html', id: 'user-link' },
    { label: 'Cerrar sesión', href: '#', dataAction: 'logout', className: 'logout' },
  ],

  tecnico: [
    { label: 'Inicio', href: '/pages/tecnico/estado-sensores' },
    { label: 'Sensores', href: '/pages/tecnico/estado-sensores.html' },
    { label: 'Incidencias', href: '/pages/gestion_incidencias.html' },
    { label: 'Mapas', href: '/pages/mapas.html' },
    { label: 'Perfil', href: '/pages/perfil.html', id: 'user-link' },
    { label: 'Cerrar sesión', href: '#', dataAction: 'logout', className: 'logout' },
  ],

  admin: [
    { label: 'Inicio', href: '/pages/admin/gestion-usuarios.html' },
    { label: 'Gestión usuarios', href: '/pages/admin/gestion-usuarios.html' },
    { label: 'Incidencias', href: '/pages/gestion_incidencias.html' },
    { label: 'Sensores', href: '/pages/tecnico/estado-sensores.html' },
    { label: 'Mapas', href: '/pages/mapas.html' },
    { label: 'Perfil', href: '/pages/perfil.html', id: 'user-link' },
    { label: 'Cerrar sesión', href: '#', dataAction: 'logout', className: 'logout' },
  ],

    tecnico_ayuntamiento: [
    { label: 'Inicio', href: '/pages/admin/gestion-usuarios.html' },
    { label: 'Gestión usuarios', href: '/pages/admin/gestion-usuarios.html' },
    { label: 'Gestión recompensas', href: '/pages/gestion_recompensas.html' },
    { label: 'Mapas', href: '/pages/mapas.html' },
    { label: 'Perfil', href: '/pages/perfil.html', id: 'user-link' },
    { label: 'Cerrar sesión', href: '#', dataAction: 'logout', className: 'logout' },
  ],
      tecnico_mapas: [
   { label: 'Inicio', href: '/pages/landing-registrado.html' },
   { label: 'Gestión mapas', href: '/pages/admin_mapas.html' },
    { label: 'Perfil', href: '/pages/perfil.html', id: 'user-link' },
    { label: 'Cerrar sesión', href: '#', dataAction: 'logout', className: 'logout' },
  ],
};

function buildNav(navElement, role) {
  const config = NAV_CONFIG[role] || NAV_CONFIG.guest;
  navElement.innerHTML = '';

  config.forEach((item) => {
    const link = document.createElement('a');
    link.href = item.href;
    link.textContent = item.label;

    if (item.className) link.classList.add(item.className);
    if (item.id) link.id = item.id;
    if (item.dataAction) link.setAttribute('data-action', item.dataAction);

    navElement.appendChild(link);
  });
}

// Menú hamburguesa: usa las clases que ya tienes en header.css
function initMenuToggle(headerRoot) {
  const toggle = headerRoot.querySelector('.menu-toggle');
  const nav = headerRoot.querySelector('.nav');
  if (!toggle || !nav) return;

  toggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  });
}

// Logout (por si añades algún enlace de logout en el futuro)
function initLogout(headerRoot) {
  const logoutLinks = headerRoot.querySelectorAll('[data-action="logout"]');
  logoutLinks.forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      logoutAndRedirect();
    });
  });
}

// Cargar nombre del usuario en el enlace de perfil
async function loadUserName(headerRoot) {
  const userLink = headerRoot.querySelector('#user-link');
  if (!userLink) return;

  const token = getToken();
  if (!token) return;

  try {
    const res = await fetch('/api/v1/perfil', {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;

    const perfil = await res.json();
    const nombre = perfil.nombre || perfil.correo || null;

    if (nombre) {
      userLink.innerHTML = `<b>${nombre}</b>`;
    }
  } catch (e) {
    console.warn('No se pudo obtener perfil para header:', e);
  }
}

async function loadHeader() {
  const container = document.getElementById('site-header');
  if (!container) return;

  try {
    const res = await fetch('/header.html');
    if (!res.ok) throw new Error('No se pudo cargar /header.html');

    const html = await res.text();
    container.innerHTML = html;

    const headerRoot = container.querySelector('.header');
    const nav = container.querySelector('#site-nav');
    if (!headerRoot || !nav) return;

    const role = isLoggedIn() ? getMainRole() : 'guest';

    buildNav(nav, role);          // pone los enlaces correctos
    initMenuToggle(headerRoot);   // hamburguesa como antes
    initLogout(headerRoot);
    if (role !== 'guest') {
      loadUserName(headerRoot);   // nombre de usuario
    }
  } catch (e) {
    console.error('[HEADER] Error cargando header:', e);
  }
}

document.addEventListener('DOMContentLoaded', loadHeader);