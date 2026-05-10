// ============================================
//   COLOURCHHEM — app.js
//   Shared sidebar, auth guard, utils
// ============================================

// ---- AUTH GUARD ----
function requireAuth() {
  const u = sessionStorage.getItem('cc_user');
  if (!u || !JSON.parse(u).loggedIn) {
    window.location.href = 'login.html';
    return null;
  }
  return JSON.parse(u);
}

// ---- API BASE ----
// Change this to your Flask server URL when connecting the backend
const API_BASE = 'http://localhost:5000';

async function apiCall(path, opts = {}) {
  try {
    const res = await fetch(API_BASE + path, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      ...opts
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  } catch (err) {
    console.error('API error:', err);
    throw err;
  }
}

// ---- TOAST ----
function showToast(msg, type = 'info') {
  let t = document.getElementById('toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg;
  t.style.background = type === 'error' ? '#c62828' : type === 'success' ? '#2e7d32' : '#1e1a2e';
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}

// ---- CURRENT PAGE ----
function currentPage() {
  return window.location.pathname.split('/').pop();
}

// ---- SIDEBAR ----
const NAV_ITEMS = [
  { href: 'dashboard.html',   label: 'Dashboard',      icon: '<rect x="3" y="3" width="8" height="8" stroke="currentColor" stroke-width="2"/><rect x="3" y="13" width="8" height="8" stroke="currentColor" stroke-width="2"/><rect x="13" y="3" width="8" height="8" stroke="currentColor" stroke-width="2"/><rect x="13" y="13" width="8" height="8" stroke="currentColor" stroke-width="2"/>' },
  { href: 'clients.html',     label: 'Clients',        icon: '<path d="M17 21V19C17 16.8 15.2 15 13 15H5C2.8 15 1 16.8 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/><path d="M23 21V19M20 15C21.7 15.5 23 17.1 23 19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>' },
  { href: 'session.html',     label: 'New Session',    icon: '<path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>' },
  { href: 'predictions.html', label: 'AI Predictions', icon: '<path d="M2 20H22M5 20V14M9 20V8M13 20V12M17 20V4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>' },
  { href: 'archive.html',     label: 'Formula Archive',icon: '<path d="M12 2L15 8L22 9L17 14L18 21L12 18L6 21L7 14L2 9L9 8L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>' },
];

function renderSidebar() {
  const el = document.getElementById('sidebar');
  if (!el) return;

  const page = currentPage();
  const logoSVG = `<svg class="sidebar-logo" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#c891d4"/>
      <stop offset="100%" style="stop-color:#6b4fa3"/>
    </linearGradient></defs>
    <path d="M100,30 Q130,40 140,70 Q145,90 140,110 Q135,130 120,145 Q105,155 100,170" fill="none" stroke="url(#sg)" stroke-width="4" stroke-linecap="round"/>
    <path d="M100,30 Q70,40 60,70 Q55,90 60,110 Q65,130 80,145 Q95,155 100,170" fill="none" stroke="url(#sg)" stroke-width="4" stroke-linecap="round"/>
    <circle cx="100" cy="25" r="8" fill="url(#sg)"/>
  </svg>`;

  const navHTML = NAV_ITEMS.map(item => `
    <li class="nav-item ${page === item.href ? 'active' : ''}">
      <a href="${item.href}">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">${item.icon}</svg>
        <span>${item.label}</span>
      </a>
    </li>`).join('');

  el.innerHTML = `
    <div class="sidebar-header">
      ${logoSVG}
      <span class="sidebar-brand">ColourChem</span>
    </div>
    <ul class="nav-menu">${navHTML}</ul>
    <div class="sidebar-footer">
      <a href="#">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/><path d="M12 16V12M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <span>Help</span>
      </a>
      <a href="#" onclick="logout()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M9 21H5C3.9 21 3 20.1 3 19V5C3 3.9 3.9 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M16 17L21 12L16 7M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <span>Logout</span>
      </a>
    </div>`;
}

async function logout() {
  // --- CONNECT BACKEND ---
  // await apiCall('/logout', { method: 'POST' });
  sessionStorage.removeItem('cc_user');
  window.location.href = 'login.html';
}

// ---- MODAL ----
function openModal(id) { document.getElementById(id).classList.add('open'); }
function closeModal(id) { document.getElementById(id).classList.remove('open'); }

// ---- INIT ----
function initApp() {
  requireAuth();
  renderSidebar();
}

// Hair level colors (reference)
const LEVEL_COLORS = {
  1:'#1a0a00', 2:'#2a1200', 3:'#3d1f00', 4:'#5c2e00',
  5:'#7a4500', 6:'#9e6010', 7:'#bf8530', 8:'#d4a855',
  9:'#e8cc80', 10:'#f5e6a8'
};