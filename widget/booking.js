/*!
 * Operaite Booking Widget
 *
 * Usage on the contractor's own website:
 *   <script async src="https://operaite.net/widget/booking.js"></script>
 *   <button data-operaite-book="your-slug">Book a service</button>
 *
 * The widget watches for clicks on any element with [data-operaite-book="<slug>"]
 * and opens an iframe modal pointing at https://operaite.net/book/<slug>?embed=1.
 *
 * Multiple buttons with different slugs on the same page are fine.
 * Modal is fully isolated CSS — no class collisions with the host page.
 */
(function () {
  'use strict';
  if (window.__operaiteBookingWidget) return; // idempotent
  window.__operaiteBookingWidget = true;

  var ORIGIN = 'https://operaite.net';
  var Z = 2147483646; // basically the top of any sane stacking context

  function injectStyles() {
    if (document.getElementById('operaite-bw-styles')) return;
    var style = document.createElement('style');
    style.id = 'operaite-bw-styles';
    style.textContent = [
      '.operaite-bw-overlay{position:fixed;inset:0;background:rgba(15,15,20,0.6);z-index:' + Z + ';display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);animation:opbw-fade 0.2s ease-out}',
      '@keyframes opbw-fade{from{opacity:0}to{opacity:1}}',
      '.operaite-bw-modal{position:relative;background:#fff;border-radius:14px;width:100%;max-width:640px;max-height:calc(100vh - 40px);overflow:hidden;box-shadow:0 24px 60px rgba(0,0,0,0.25);display:flex;flex-direction:column;animation:opbw-slide 0.25s cubic-bezier(0.2,0.8,0.2,1)}',
      '@keyframes opbw-slide{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}',
      '.operaite-bw-close{position:absolute;top:10px;right:10px;width:32px;height:32px;border-radius:50%;background:rgba(0,0,0,0.55);color:#fff;border:none;cursor:pointer;font-size:18px;line-height:1;z-index:2;display:flex;align-items:center;justify-content:center;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}',
      '.operaite-bw-close:hover{background:rgba(0,0,0,0.75)}',
      '.operaite-bw-iframe{flex:1;width:100%;border:0;background:#fff;min-height:520px}',
      '.operaite-bw-loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#888;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;font-size:14px;background:#fff;z-index:1}',
      '@media (max-width: 700px){.operaite-bw-overlay{padding:0}.operaite-bw-modal{max-width:100vw;max-height:100vh;border-radius:0}.operaite-bw-iframe{min-height:0}}'
    ].join('');
    document.head.appendChild(style);
  }

  function openModal(slug) {
    if (!slug) return;
    injectStyles();
    var overlay = document.createElement('div');
    overlay.className = 'operaite-bw-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.innerHTML = '' +
      '<div class="operaite-bw-modal">' +
        '<button type="button" class="operaite-bw-close" aria-label="Close">×</button>' +
        '<div class="operaite-bw-loading">Loading…</div>' +
        '<iframe class="operaite-bw-iframe" src="' + ORIGIN + '/book/' + encodeURIComponent(slug) + '?embed=1" allow="clipboard-write" referrerpolicy="strict-origin-when-cross-origin"></iframe>' +
      '</div>';

    function close() {
      window.removeEventListener('message', onMsg);
      document.removeEventListener('keydown', onKey);
      overlay.remove();
      // Restore body scroll
      document.body.style.overflow = '';
    }

    function onMsg(e) {
      if (!e || !e.data) return;
      // Validate origin so a malicious page can't spoof close events
      if (e.origin !== ORIGIN) return;
      if (e.data && e.data.type === 'operaite-booking-close') close();
    }

    function onKey(e) {
      if (e.key === 'Escape') close();
    }

    overlay.querySelector('.operaite-bw-close').addEventListener('click', close);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) close(); });
    overlay.querySelector('.operaite-bw-iframe').addEventListener('load', function () {
      var loading = overlay.querySelector('.operaite-bw-loading');
      if (loading) loading.remove();
    });

    window.addEventListener('message', onMsg);
    document.addEventListener('keydown', onKey);
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
  }

  function onClick(e) {
    var el = e.target.closest('[data-operaite-book]');
    if (!el) return;
    e.preventDefault();
    var slug = el.getAttribute('data-operaite-book');
    if (!slug) return;
    openModal(slug);
  }

  // Bind once at the document level so dynamically-added buttons work
  document.addEventListener('click', onClick);

  // Also expose a programmatic API for advanced users
  window.OperaiteBooking = {
    open: openModal,
    version: '1.0.0'
  };
})();
