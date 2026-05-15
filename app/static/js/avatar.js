// ============================================
//   COLOURCHHEM — avatar.js
//   Shares sidebar, topbar with each page
// ============================================


async function loadSidebarAvatar() {
  const sbAv = document.getElementById('sbAv');
  const tbAv = document.getElementById('tbAv');
  if (!sbAv && !tbAv) return; // not on a page with these elements

  try {
    const res = await fetch('/avatar-url');
    const data = await res.json();
    if (!data.image_url) return;

    [
      { container: 'sbAv', initial: 'sbAvInitial', img: 'sbAvImg' },
      { container: 'tbAv', initial: 'tbAvInitial', img: 'tbAvImg' }
    ].forEach(({ initial, img }) => {
      const imgEl = document.getElementById(img);
      const initEl = document.getElementById(initial);
      if (!imgEl || !initEl) return;
      imgEl.src = data.image_url;
      imgEl.style.display = 'block';
      initEl.style.display = 'none';
    });
  } catch(e) {
    console.error('Could not load sidebar avatar:', e);
  }
}

document.addEventListener('DOMContentLoaded', loadSidebarAvatar);