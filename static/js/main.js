// Main JavaScript for Personal Blog

(function () {
    'use strict';

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : null;
    }

    function getCsrfToken() {
        return getCookie('csrftoken') || '';
    }

    async function csrfPost(url, data) {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(data || {}),
            credentials: 'same-origin',
        });
        let payload = null;
        try {
            payload = await res.json();
        } catch (e) {
            payload = null;
        }
        return { ok: res.ok, status: res.status, payload };
    }

    // Copy link button in share modal
    document.addEventListener('click', function (e) {
        if (e.target.matches('[data-copy-link-button]') || e.target.closest('[data-copy-link-button]')) {
            const btn = e.target.matches('[data-copy-link-button]') ? e.target : e.target.closest('[data-copy-link-button]');
            const input = btn.closest('.input-group')?.querySelector('input');
            if (input) {
                input.select();
                navigator.clipboard.writeText(input.value).then(() => {
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
                }).catch(() => {
                    document.execCommand('copy');
                    btn.textContent = 'Copied!';
                    setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
                });
            }
        }
    });

    // AJAX like toggle
    document.querySelectorAll('[data-like-url]').forEach(function (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const btn = form.querySelector('button[type="submit"]');
            const url = form.getAttribute('data-like-url');
            const res = await csrfPost(url, { post_id: parseInt(form.getAttribute('data-post-id') || '0', 10) });
            if (res.ok) {
                const liked = btn.classList.contains('btn-danger');
                btn.classList.toggle('btn-danger', !liked);
                btn.classList.toggle('btn-outline-danger', liked);
                btn.innerHTML = liked ? '<i class="bi bi-heart"></i> Like' : '<i class="bi bi-heart-fill"></i> Unlike';
            }
        });
    });

    // AJAX bookmark toggle
    document.querySelectorAll('[data-bookmark-url]').forEach(function (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const btn = form.querySelector('button[type="submit"]');
            const url = form.getAttribute('data-bookmark-url');
            const res = await csrfPost(url, { post_id: parseInt(form.getAttribute('data-post-id') || '0', 10) });
            if (res.ok) {
                const saved = btn.classList.contains('btn-success');
                btn.classList.toggle('btn-success', !saved);
                btn.classList.toggle('btn-outline-success', saved);
                btn.innerHTML = saved ? '<i class="bi bi-bookmark"></i> Save' : '<i class="bi bi-bookmark-fill"></i> Saved';
            }
        });
    });

    // Reading time estimator
    function computeReadingTime(text) {
        if (!text) return '0 min read';
        const words = String(text).trim().split(/\s+/).filter(Boolean).length;
        const minutes = Math.max(1, Math.round(words / 200));
        return minutes + ' min read';
    }

    function attachReadingTime() {
        const contentEl = document.querySelector('#id_content, textarea[name="content"]');
        const outEl = document.querySelector('#readingTimeOutput');
        if (!contentEl || !outEl) return;
        const update = () => { outEl.textContent = computeReadingTime(contentEl.value); };
        contentEl.addEventListener('input', update);
        update();
    }

    document.addEventListener('DOMContentLoaded', function () {
        attachReadingTime();
    });
})();
