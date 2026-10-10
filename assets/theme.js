(function () {
  'use strict';

  const moneyFormat = (window.SilkyNest && window.SilkyNest.moneyFormat) || 'Rs.{{amount}}';
  const routes = (window.SilkyNest && window.SilkyNest.routes) || {
    cart_add_url: '/cart/add.js',
    cart_change_url: '/cart/change.js',
    cart_url: '/cart',
    root: '/'
  };

  function formatMoney(cents) {
    if (typeof cents === 'string') cents = cents.replace('.', '');
    const value = (Number(cents) / 100).toFixed(2);
    const parts = value.split('.');
    try {
      return moneyFormat
        .replace(/\{\{\s*amount\s*\}\}/g, Number(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }))
        .replace(/\{\{\s*amount_no_decimals\s*\}\}/g, Number(parts[0]).toLocaleString())
        .replace(/\{\{\s*amount_with_comma_separator\s*\}\}/g, value.replace('.', ','))
        .replace(/\{\{\s*amount_no_decimals_with_comma_separator\s*\}\}/g, parts[0]);
    } catch (e) {
      return 'Rs.' + Number(parts[0]).toLocaleString();
    }
  }

  function qs(sel, ctx) {
    return (ctx || document).querySelector(sel);
  }

  function qsa(sel, ctx) {
    return Array.from((ctx || document).querySelectorAll(sel));
  }

  /* Header scroll state -------------------------------------------------- */
  const header = qs('[data-site-header]');
  if (header) {
    const onScroll = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 8);
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* Mobile nav ----------------------------------------------------------- */
  const navToggle = qs('[data-nav-toggle]');
  const mobileNav = qs('[data-mobile-nav]');
  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', () => {
      const open = mobileNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* Reveal on scroll ----------------------------------------------------- */
  const revealEls = qsa('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-visible'));
  }

  /* Hero / product image slider ------------------------------------------ */
  function initSlider(root) {
    if (!root) return;
    const track = qs('[data-slider-track]', root);
    const slides = qsa('[data-slider-slide]', root);
    const dots = qsa('[data-slider-dot]', root);
    const prev = qs('[data-slider-prev]', root);
    const next = qs('[data-slider-next]', root);
    const label = qs('[data-slider-label]', root);
    if (!track || !slides.length) return;

    let index = 0;
    let timer;

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = 'translateX(' + (-index * 100) + '%)';
      slides.forEach((s, n) => s.classList.toggle('is-active', n === index));
      dots.forEach((d, n) => d.classList.toggle('is-active', n === index));
      if (label) {
        const text = slides[index].getAttribute('data-label');
        if (text) label.textContent = text;
      }
    }

    function startAuto() {
      stopAuto();
      timer = window.setInterval(() => goTo(index + 1), 4500);
    }

    function stopAuto() {
      if (timer) window.clearInterval(timer);
    }

    dots.forEach((dot, i) => {
      dot.addEventListener('click', () => {
        goTo(i);
        startAuto();
      });
    });

    if (prev) prev.addEventListener('click', () => { goTo(index - 1); startAuto(); });
    if (next) next.addEventListener('click', () => { goTo(index + 1); startAuto(); });

    root.addEventListener('mouseenter', stopAuto);
    root.addEventListener('mouseleave', startAuto);

    let startX = 0;
    track.addEventListener('touchstart', (e) => {
      startX = e.changedTouches[0].clientX;
      stopAuto();
    }, { passive: true });

    track.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) goTo(dx < 0 ? index + 1 : index - 1);
      startAuto();
    }, { passive: true });

    goTo(0);
    startAuto();
  }

  qsa('[data-hero-slider], [data-product-slider]').forEach(initSlider);

  /* Reviews featured slider ---------------------------------------------- */
  qsa('[data-reviews]').forEach((root) => {
    const slides = qsa('[data-review-slide]', root);
    const dots = qsa('[data-review-dot]', root);
    const prev = qs('[data-review-prev]', root);
    const next = qs('[data-review-next]', root);
    const count = qs('[data-review-count]', root);
    if (!slides.length) return;

    let index = 0;

    function pad(n) {
      return (n < 10 ? '0' : '') + n;
    }

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      slides.forEach((slide, n) => {
        const active = n === index;
        slide.classList.toggle('is-active', active);
        if (active) slide.removeAttribute('hidden');
        else slide.setAttribute('hidden', '');
      });
      dots.forEach((dot, n) => dot.classList.toggle('is-active', n === index));
      if (count) count.textContent = pad(index + 1) + ' / ' + pad(slides.length);
    }

    if (prev) prev.addEventListener('click', () => goTo(index - 1));
    if (next) next.addEventListener('click', () => goTo(index + 1));
    dots.forEach((dot, i) => dot.addEventListener('click', () => goTo(i)));

    let startX = 0;
    root.addEventListener('touchstart', (e) => {
      startX = e.changedTouches[0].clientX;
    }, { passive: true });
    root.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) goTo(dx < 0 ? index + 1 : index - 1);
    }, { passive: true });

    goTo(0);
  });

  /* Product gallery thumbs ----------------------------------------------- */
  qsa('[data-product-gallery]').forEach((gallery) => {
    const main = qs('[data-gallery-main]', gallery);
    const thumbs = qsa('[data-gallery-thumb]', gallery);
    thumbs.forEach((thumb) => {
      thumb.addEventListener('click', () => {
        const src = thumb.getAttribute('data-full');
        const alt = thumb.getAttribute('data-alt') || '';
        if (main && src) {
          main.src = src;
          main.alt = alt;
        }
        thumbs.forEach((t) => t.classList.remove('is-active'));
        thumb.classList.add('is-active');
      });
    });
  });

  /* Quantity selectors --------------------------------------------------- */
  function bindQty(root) {
    qsa('[data-qty]', root || document).forEach((wrap) => {
      const input = qs('input', wrap);
      const minus = qs('[data-qty-minus]', wrap);
      const plus = qs('[data-qty-plus]', wrap);
      if (!input) return;
      if (minus) {
        minus.addEventListener('click', () => {
          const val = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
          input.value = val;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      }
      if (plus) {
        plus.addEventListener('click', () => {
          const max = parseInt(input.max, 10) || 99;
          const val = Math.min(max, (parseInt(input.value, 10) || 1) + 1);
          input.value = val;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
      }
    });
  }
  bindQty();

  /* FAQ accordion -------------------------------------------------------- */
  qsa('[data-faq-item]').forEach((item) => {
    const btn = qs('[data-faq-toggle]', item);
    if (!btn) return;
    btn.addEventListener('click', () => {
      const open = item.classList.contains('is-open');
      qsa('[data-faq-item]').forEach((other) => {
        other.classList.remove('is-open');
        const b = qs('[data-faq-toggle]', other);
        if (b) b.setAttribute('aria-expanded', 'false');
      });
      if (!open) {
        item.classList.add('is-open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* Toast ---------------------------------------------------------------- */
  function showToast(message) {
    const toast = qs('[data-toast]');
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    requestAnimationFrame(() => toast.classList.add('is-visible'));
    window.setTimeout(() => {
      toast.classList.remove('is-visible');
      window.setTimeout(() => { toast.hidden = true; }, 350);
    }, 2400);
  }

  /* Cart drawer ---------------------------------------------------------- */
  const drawer = qs('[data-cart-drawer]');
  const overlay = qs('[data-cart-overlay]');
  const cartBody = qs('[data-cart-body]');
  const cartFooter = qs('[data-cart-footer]');
  const cartSubtotal = qs('[data-cart-subtotal]');
  const cartCountEls = qsa('[data-cart-count]');

  function openCart() {
    if (!drawer || !overlay) return;
    overlay.hidden = false;
    requestAnimationFrame(() => {
      overlay.classList.add('is-open');
      drawer.classList.add('is-open');
      drawer.setAttribute('aria-hidden', 'false');
    });
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    if (!drawer || !overlay) return;
    overlay.classList.remove('is-open');
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    window.setTimeout(() => { overlay.hidden = true; }, 350);
  }

  qsa('[data-cart-open]').forEach((btn) => btn.addEventListener('click', openCart));
  qsa('[data-cart-close]').forEach((btn) => btn.addEventListener('click', closeCart));
  if (overlay) overlay.addEventListener('click', closeCart);

  function updateCartCount(count) {
    cartCountEls.forEach((el) => {
      el.textContent = String(count);
      el.hidden = count < 1;
    });
  }

  function renderCart(cart) {
    if (!cartBody) return;
    updateCartCount(cart.item_count || 0);

    if (!cart.items || !cart.items.length) {
      cartBody.innerHTML = '<p class="cart-drawer__empty">Your bag is empty.</p>';
      if (cartFooter) cartFooter.hidden = true;
      return;
    }

    cartBody.innerHTML = cart.items.map((item) => {
      const img = item.image
        ? '<img src="' + item.image + '" alt="' + (item.product_title || '').replace(/"/g, '&quot;') + '">'
        : '<div></div>';
      return (
        '<div class="cart-item">' +
          img +
          '<div>' +
            '<div class="cart-item__title">' + item.product_title + '</div>' +
            '<div class="cart-item__meta">Qty ' + item.quantity + ' · ' + formatMoney(item.final_line_price) + '</div>' +
          '</div>' +
          '<button type="button" aria-label="Remove" data-remove-key="' + item.key + '">' +
            '<svg width="16" height="16" viewBox="0 0 20 20" fill="none"><path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="1.5"/></svg>' +
          '</button>' +
        '</div>'
      );
    }).join('');

    if (cartFooter) cartFooter.hidden = false;
    if (cartSubtotal) cartSubtotal.textContent = formatMoney(cart.total_price);

    qsa('[data-remove-key]', cartBody).forEach((btn) => {
      btn.addEventListener('click', async () => {
        const key = btn.getAttribute('data-remove-key');
        await fetch(routes.cart_change_url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ id: key, quantity: 0 })
        });
        const updated = await fetchCart();
        renderCart(updated);
      });
    });
  }

  async function fetchCart() {
    const res = await fetch('/cart.js', { headers: { Accept: 'application/json' } });
    return res.json();
  }

  fetchCart().then(renderCart).catch(() => {});

  /* Add to cart forms ---------------------------------------------------- */
  async function addToCart(variantId, quantity, opts) {
    opts = opts || {};
    const res = await fetch(routes.cart_add_url + '.js', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ id: Number(variantId), quantity: Number(quantity) || 1 })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.description || 'Unable to add to cart');
    }

    const cart = await fetchCart();
    renderCart(cart);
    showToast('Added to your bag');

    if (opts.buyNow) {
      window.location.href = '/checkout';
      return;
    }

    if (opts.openDrawer !== false) openCart();
  }

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('[data-product-form]');
    if (!form) return;
    e.preventDefault();

    const variantInput = qs('[name="id"]', form);
    const qtyInput = qs('[name="quantity"]', form);
    const buyNow = e.submitter && e.submitter.hasAttribute('data-buy-now');
    const btn = e.submitter || qs('[type="submit"]', form);

    if (!variantInput || !variantInput.value) {
      showToast('Product unavailable');
      return;
    }

    const original = btn ? btn.textContent : '';
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Adding…';
    }

    try {
      await addToCart(variantInput.value, qtyInput ? qtyInput.value : 1, { buyNow: buyNow });
    } catch (err) {
      showToast(err.message || 'Something went wrong');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = original;
      }
    }
  });

  /* Sticky ATC visibility ------------------------------------------------ */
  const sticky = qs('[data-sticky-atc]');
  const productForm = qs('[data-product-form-anchor], [data-featured-product]');
  if (sticky && productForm && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        sticky.classList.toggle('is-visible', !entry.isIntersecting && entry.boundingClientRect.top < 0);
      });
    }, { threshold: 0 });
    io.observe(productForm);
  }

  /* Smooth anchor links -------------------------------------------------- */
  qsa('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const id = link.getAttribute('href');
      if (!id || id === '#') return;
      const target = qs(id);
      if (!target) return;
      e.preventDefault();
      const offset = (header ? header.offsetHeight : 0) + 12;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: top, behavior: 'smooth' });
      if (mobileNav) mobileNav.classList.remove('is-open');
    });
  });
})();
