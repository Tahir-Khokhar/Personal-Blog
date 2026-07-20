// App-level JS (AJAX helpers + UI utilities)

(function () {
  function getCsrfToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
  }

  async function apiPost(url, data) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(data || {}),
    });
    let payload = null;
    try {
      payload = await res.json();
    } catch (e) {
      payload = null;
    }
    return { res, payload };
  }

  function attachLikeToggles() {
    document.querySelectorAll('[data-like-post-id]').forEach((btn) => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';

      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const postId = btn.getAttribute('data-like-post-id');
        if (!postId) return;

        // Backend already prevents duplicates (toggle behavior) on the API side.
        const url = btn.getAttribute('data-like-url') || '/post/like-post/';
        const { res, payload } = await apiPost(url, { post_id: Number(postId) });

        if (!res.ok) {
          alert((payload && payload.message) || 'Action failed');
          return;
        }

        // UI update (optimistic toggle label)
        const liked = btn.getAttribute('data-liked') === '1';
        const nextLiked = !liked;
        btn.setAttribute('data-liked', nextLiked ? '1' : '0');
        btn.classList.toggle('btn-danger', nextLiked);
        btn.classList.toggle('btn-outline-danger', !nextLiked);
        btn.innerText = nextLiked ? 'Unlike' : 'Like';
      });
    });
  }

  function attachBookmarkToggles() {
    document.querySelectorAll('[data-bookmark-post-id]').forEach((btn) => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';

      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const postId = btn.getAttribute('data-bookmark-post-id');
        if (!postId) return;

        const url = btn.getAttribute('data-bookmark-url') || '/post/bookmark-post/';
        const { res, payload } = await apiPost(url, { post_id: Number(postId) });
        if (!res.ok) {
          alert((payload && payload.message) || 'Action failed');
          return;
        }

        const saved = btn.getAttribute('data-saved') === '1';
        const nextSaved = !saved;
        btn.setAttribute('data-saved', nextSaved ? '1' : '0');
        btn.classList.toggle('btn-success', nextSaved);
        btn.classList.toggle('btn-outline-success', !nextSaved);
        btn.innerText = nextSaved ? 'Saved' : 'Save';
      });
    });
  }

  function computeReadingTime(text) {
    if (!text) return '0 min';
    const words = String(text).trim().split(/\s+/).filter(Boolean).length;
    const minutes = Math.max(1, Math.round(words / 200)); // ~200 wpm
    return minutes + ' min read';
  }

  function attachReadingTime() {
    const contentEl = document.querySelector('#id_content, textarea[name="content"]');
    const outEl = document.querySelector('#readingTimeOutput');
    if (!contentEl || !outEl) return;

    const update = () => {
      outEl.textContent = computeReadingTime(contentEl.value);
    };
    contentEl.addEventListener('input', update);
    update();
  }

  function attachShareButtons() {
    document.querySelectorAll('[data-share-url]').forEach((btn) => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';

      btn.addEventListener('click', async (e) => {
        e.preventDefault();
        const url = btn.getAttribute('data-share-url');
        const title = btn.getAttribute('data-share-title') || document.title;
        if (!url) return;

        // Clipboard copy
        const copyBtn = document.querySelector('[data-copy-link-button]');
        if (copyBtn) {
          copyBtn.onclick = async () => {
            try {
              await navigator.clipboard.writeText(url);
              alert('Link copied!');
            } catch {
              prompt('Copy link:', url);
            }
          };
        }

        // Open share targets
        const facebook = document.querySelector('[data-share-facebook]');
        if (facebook) facebook.href = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;

        const x = document.querySelector('[data-share-x]');
        if (x) x.href = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;

        const whatsapp = document.querySelector('[data-share-whatsapp]');
        if (whatsapp) whatsapp.href = `https://wa.me/?text=${encodeURIComponent(url)}`;

        const linkedin = document.querySelector('[data-share-linkedin]');
        if (linkedin) linkedin.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;

        const telegram = document.querySelector('[data-share-telegram]');
        if (telegram) telegram.href = `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;

        // Show modal if present
        const modalEl = document.querySelector('#shareModal');
        if (modalEl && window.bootstrap) {
          window.bootstrap.Modal.getOrCreateInstance(modalEl).show();
        }
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    attachLikeToggles();
    attachBookmarkToggles();
    attachReadingTime();
    attachShareButtons();
  });
})();

