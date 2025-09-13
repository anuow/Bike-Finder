// static/js/wishlist.js
document.addEventListener('DOMContentLoaded', () => {
  // avoid double-attaching if script loaded twice
  if (window.__wishlistHandlerAttached) return;
  window.__wishlistHandlerAttached = true;

  function showToast(msg, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3`;
    toast.style.zIndex = 9999;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }

  document.body.addEventListener('click', async (e) => {
    const btn = e.target.closest('.add-to-wishlist');
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    // Protect against accidental double clicks
    if (btn.dataset.pending === 'true') return;
    btn.dataset.pending = 'true';

    try {
      const make = btn.dataset.make;
      const model = btn.dataset.model;
      if (!make || !model) {
        showToast('Missing bike data.', 'danger');
        return;
      }

      const formData = new FormData();
      formData.append('bike_make', make);
      formData.append('bike_model', model);

      const res = await fetch('/add_to_wishlist', {
        method: 'POST',
        headers: {
          // Let backend detect this as AJAX (so it returns JSON, not an HTML redirect)
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData,
        redirect: 'follow'
      });

      // read as text first (safe if server returned HTML)
      const text = await res.text();
      let data = null;
      try {
        data = JSON.parse(text);
      } catch (err) {
        data = null;
      }

      if (data && typeof data.success !== 'undefined') {
        if (data.success) {
          // update button UI based on action
          if (data.action === 'added') {
            btn.textContent = '✔ Added';
            btn.classList.remove('btn-outline-danger');
            btn.classList.add('btn-success');
          } else if (data.action === 'removed') {
            btn.textContent = '♥ Add to Wishlist';
            btn.classList.remove('btn-success');
            btn.classList.add('btn-outline-danger');
          }
          showToast(data.message || 'Updated wishlist.', 'success');
        } else {
          showToast(data.message || 'Action failed.', 'danger');
        }
      } else {
        // server returned HTML (probably a redirect). Reload so UI matches server state.
        window.location.reload();
      }
    } catch (err) {
      console.error('Wishlist network error', err);
      showToast('Network error. Try again.', 'danger');
    } finally {
      btn.dataset.pending = 'false';
    }
  });
});
