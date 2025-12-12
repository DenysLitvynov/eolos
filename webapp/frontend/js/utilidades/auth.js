// Devuelve el token guardado
export function getToken() {
  return localStorage.getItem('token') || sessionStorage.getItem('token') || null;
}

// Decodifica un JWT
export function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    console.error('Error al decodificar JWT:', e);
    return null;
  }
}

export function getDecodedToken() {
  const token = getToken();
  if (!token) return null;
  return parseJwt(token);
}

export function getUserRoles() {
  const decoded = getDecodedToken();
  if (!decoded || !Array.isArray(decoded.roles)) return [];
  return decoded.roles;
}

export function getMainRole() {
  const roles = getUserRoles();
  
  // 1) admin general manda sobre todo
  if (roles.includes('admin')) return 'admin';

  // 2) roles más específicos
  if (roles.includes('tecnico_mapas')) return 'tecnico_mapas';
  if (roles.includes('tecnico_ayuntamiento')) return 'tecnico_ayuntamiento';
  if (roles.includes('tecnico')) return 'tecnico';

  // 3) usuario normal
  if (roles.includes('usuario')) return 'usuario';

  // 4) sin rol conocido → invitado
  return 'guest';
}

export function isLoggedIn() {
  return !!getDecodedToken();
}

export function logoutAndRedirect() {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
  window.location.href = '/index.html';
}