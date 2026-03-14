// ========================================
// Jleray-Relay — Global JS utilities
// ========================================

// ── Toast notification system ──
const Toast = {
  container: null,
  init() {
    if (this.container) return;
    this.container = document.createElement('div');
    this.container.id = 'toast-container';
    this.container.style.cssText = `
      position: fixed; bottom: 1.5rem; right: 1.5rem;
      z-index: 9999; display: flex; flex-direction: column-reverse;
      gap: 0.6rem; pointer-events: none;
    `;
    document.body.appendChild(this.container);
  },
  show(message, type = 'success', duration = 3500) {
    this.init();
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const colors = {
      success: { bg: 'rgba(0,230,118,0.12)', border: 'rgba(0,230,118,0.35)', color: '#00e676' },
      error:   { bg: 'rgba(255,82,82,0.12)',  border: 'rgba(255,82,82,0.35)',  color: '#ff5252' },
      info:    { bg: 'rgba(0,217,255,0.12)',  border: 'rgba(0,217,255,0.35)',  color: '#00d9ff' },
      warning: { bg: 'rgba(255,215,64,0.12)', border: 'rgba(255,215,64,0.35)', color: '#ffd740' },
    };
    const c = colors[type] || colors.info;
    const el = document.createElement('div');
    el.style.cssText = `
      background: ${c.bg}; border: 1px solid ${c.border}; color: ${c.color};
      border-radius: 12px; padding: 0.75rem 1.2rem;
      font-family: Inter, sans-serif; font-size: 0.88rem; font-weight: 600;
      backdrop-filter: blur(20px); pointer-events: auto;
      display: flex; align-items: center; gap: 0.6rem;
      box-shadow: 0 8px 30px rgba(0,0,0,0.4);
      transform: translateX(110%); transition: transform 0.35s cubic-bezier(0.22,1,0.36,1), opacity 0.3s;
      max-width: 340px; word-break: break-word;
    `;
    el.innerHTML = `<span>${icons[type] || '•'}</span><span>${message}</span>`;
    this.container.appendChild(el);
    requestAnimationFrame(() => { el.style.transform = 'translateX(0)'; });
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(110%)';
      setTimeout(() => el.remove(), 350);
    }, duration);
  }
};

// ── Confirm dialog (styled) ──
function relayConfirm(message) {
  return new Promise(resolve => {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
      position: fixed; inset: 0; z-index: 9998;
      background: rgba(0,0,0,0.6); backdrop-filter: blur(6px);
      display: flex; align-items: center; justify-content: center;
    `;
    overlay.innerHTML = `
      <div style="
        background: #16213e; border: 1px solid #2a2a4a;
        border-radius: 18px; padding: 2rem; max-width: 380px; width: 90%;
        box-shadow: 0 25px 60px rgba(0,0,0,0.5);
        animation: scaleIn 0.25s cubic-bezier(0.22,1,0.36,1) both;
      ">
        <div style="font-size:2rem; margin-bottom:1rem; text-align:center">⚠️</div>
        <p style="color:#e8e8f0; font-family:Inter,sans-serif; text-align:center; margin-bottom:1.5rem; line-height:1.5">${message}</p>
        <div style="display:flex; gap:0.8rem; justify-content:center">
          <button id="confirm-cancel" style="
            padding:0.6rem 1.5rem; border-radius:10px; border:1px solid #2a2a4a;
            background:#1a1a2e; color:#8888aa; font-family:Inter,sans-serif;
            font-size:0.9rem; cursor:pointer; transition:all 0.2s;
          ">Annuler</button>
          <button id="confirm-ok" style="
            padding:0.6rem 1.5rem; border-radius:10px; border:none;
            background:linear-gradient(135deg,#ff5252,#ff1744); color:white;
            font-family:Inter,sans-serif; font-size:0.9rem;
            font-weight:700; cursor:pointer; transition:all 0.2s;
            box-shadow: 0 4px 15px rgba(255,82,82,0.35);
          ">Confirmer</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    overlay.querySelector('#confirm-cancel').onclick = () => { overlay.remove(); resolve(false); };
    overlay.querySelector('#confirm-ok').onclick = () => { overlay.remove(); resolve(true); };
    overlay.onclick = (e) => { if (e.target === overlay) { overlay.remove(); resolve(false); } };
  });
}

// Inject scaleIn keyframe
const style = document.createElement('style');
style.textContent = `@keyframes scaleIn { from{opacity:0;transform:scale(0.9)} to{opacity:1;transform:scale(1)} }`;
document.head.appendChild(style);

window.Toast = Toast;
window.relayConfirm = relayConfirm;
