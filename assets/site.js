/* 玺爱珠宝中文站 — 菜单、珠宝下拉、品牌影片、首页轮播、产品图库、筛选、咨询预填。
   XIAI JEWELRY (Chinese site) — menu, jewellery dropdown, brand film, home carousel,
   product gallery, filters, enquiry prefill */
(function () {
  var doc = document;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');

  var still = function () { return !!(reduceMotion && reduceMotion.matches); };

  // Brand film (last slide of the home carousel): muted loop with our own
  // pause and sound buttons. It loads and plays only while its slide is open
  // and on screen, and never starts by itself for reduced-motion visitors.
  var filmApi = null;
  var film = doc.getElementById('film');
  if (film) {
    var frame = film.parentNode;
    var playBtn = frame.querySelector('.film-play');
    var soundBtn = frame.querySelector('.film-sound');
    var wanted = false, onScreen = true, userPaused = false;
    film.removeAttribute('controls');
    frame.classList.add('js-film');
    var syncPlay = function () {
      playBtn.classList.toggle('is-paused', film.paused);
      playBtn.setAttribute('aria-label', film.paused ? '播放影片' : '暂停影片');
    };
    var syncSound = function () {
      soundBtn.classList.toggle('is-on', !film.muted);
      soundBtn.setAttribute('aria-label', film.muted ? '打开声音' : '关闭声音');
    };
    var start = function () {
      var p = film.play();
      if (p && p.catch) { p.catch(syncPlay); }
    };
    var update = function () {
      if (wanted && onScreen && !userPaused && !still()) { if (film.paused) { start(); } }
      else if (!film.paused && (!wanted || !onScreen)) { film.pause(); }
    };
    film.addEventListener('play', syncPlay);
    film.addEventListener('pause', syncPlay);
    film.addEventListener('volumechange', syncSound);
    playBtn.addEventListener('click', function () {
      if (film.paused) { userPaused = false; start(); } else { userPaused = true; film.pause(); }
    });
    soundBtn.addEventListener('click', function () {
      film.muted = !film.muted;
      if (!film.muted && film.paused) { userPaused = false; start(); }
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { onScreen = en.isIntersecting; update(); });
      }, { threshold: 0.25 }).observe(film);
    }
    syncPlay();
    syncSound();
    filmApi = { show: function (on) { wanted = on; update(); }, slide: film.closest('.slide') };
  }

  // Home carousel: edge to edge, native swipe with snap, arrows, dots and
  // arrow keys. Plays through the pictures by itself (6 s each) and stops on
  // the film; any touch, click, key press or sideways swipe hands control to
  // the visitor for good. It also waits while off screen or in a hidden tab.
  doc.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.car-track');
    var slides = [].slice.call(track.children);
    var dots = car.querySelectorAll('.car-dots button');
    var prev = car.querySelector('.car-btn.prev');
    var next = car.querySelector('.car-btn.next');
    car.classList.add('js');
    // Fill the screen under the announcement bar and header.
    var bar = doc.querySelector('.bar');
    var siteHeader = doc.querySelector('.site-header');
    var setChrome = function () {
      var h = (bar ? bar.offsetHeight : 0) + (siteHeader ? siteHeader.offsetHeight : 0);
      doc.documentElement.style.setProperty('--chrome', h + 'px');
    };
    setChrome();
    window.addEventListener('resize', setChrome);

    var current = -1, timer = null, auto = !still(), visible = true;
    var activate = function (i) {
      if (i === current) { return; }
      current = i;
      slides.forEach(function (sl, k) { sl.classList.toggle('is-active', k === i); });
      dots.forEach(function (d, k) {
        if (k === i) { d.setAttribute('aria-current', 'true'); } else { d.removeAttribute('aria-current'); }
      });
      if (filmApi) { filmApi.show(slides[i] === filmApi.slide); }
      schedule();
    };
    var show = function (i) {
      var n = slides.length;
      i = (i % n + n) % n;
      track.scrollTo({ left: i * track.clientWidth, behavior: still() ? 'auto' : 'smooth' });
    };
    var schedule = function () {
      clearTimeout(timer);
      var sl = slides[current];
      if (!auto || !visible || doc.hidden || !sl || (filmApi && sl === filmApi.slide)) { return; }
      timer = setTimeout(function () { show(current + 1); }, 6000);
    };
    var takeOver = function () { auto = false; clearTimeout(timer); };
    var index = function () { return Math.round(track.scrollLeft / Math.max(track.clientWidth, 1)); };
    track.addEventListener('scroll', function () { activate(index()); }, { passive: true });
    ['pointerdown', 'touchstart', 'keydown', 'focusin'].forEach(function (ev) {
      car.addEventListener(ev, takeOver, { passive: true });
    });
    car.addEventListener('wheel', function (e) {
      if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) { takeOver(); }
    }, { passive: true });
    doc.addEventListener('visibilitychange', schedule);
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        schedule();
      }, { threshold: 0.4 }).observe(car);
    }
    if (prev && next) {
      prev.addEventListener('click', function () { show(current - 1); });
      next.addEventListener('click', function () { show(current + 1); });
    }
    dots.forEach(function (d, k) { d.addEventListener('click', function () { show(k); }); });
    car.addEventListener('keydown', function (e) {
      if (e.target.closest && e.target.closest('a')) { return; }
      if (e.key === 'ArrowLeft') { e.preventDefault(); show(current - 1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); show(current + 1); }
    });
    // Let the first slide's text rise in just after the page first paints.
    setTimeout(function () { activate(index()); }, 80);
  });

  // "As worn" strip: arrows page through the photos on wide screens.
  doc.querySelectorAll('[data-strip]').forEach(function (box) {
    var strip = box.querySelector('.strip');
    var prev = box.querySelector('.strip-btn.prev');
    var next = box.querySelector('.strip-btn.next');
    if (!strip || !prev || !next) { return; }
    box.classList.add('js');
    var sync = function () {
      var max = strip.scrollWidth - strip.clientWidth - 2;
      prev.setAttribute('aria-disabled', strip.scrollLeft <= 2 ? 'true' : 'false');
      next.setAttribute('aria-disabled', strip.scrollLeft >= max ? 'true' : 'false');
    };
    var step = function (dir) {
      strip.scrollBy({ left: dir * strip.clientWidth * 0.8, behavior: still() ? 'auto' : 'smooth' });
    };
    prev.addEventListener('click', function () { step(-1); });
    next.addEventListener('click', function () { step(1); });
    strip.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  });

  // Scroll-in effects (after xueluopearl.com, with a little bounce): blocks
  // below the first screen rise into place as they come into view, side-by-side
  // items one after another, and headings character by character.
  // 标题逐字跳出：每个汉字一个节拍；英文单词和数字整体跳出；标点跟着前一个字，
  // 开引号/括号跟着后一个字，这样换行时行首不会出现“，”。
  var CJK = /[\u3400-\u9fff\uf900-\ufaff]/;
  var CLOSE = '，。、：；！？”’》）)…·';
  var OPEN = '“‘《（(';
  var STEP = 45; // ms between characters, matches site.css
  var pieces = function (text) {
    var out = [], pre = '', latin = false;
    for (var i = 0; i < text.length; i++) {
      var ch = text.charAt(i);
      if (/\s/.test(ch)) { if (out.length && out[out.length - 1] !== ' ') { out.push(' '); } latin = false; continue; }
      if (CLOSE.indexOf(ch) > -1 && out.length && out[out.length - 1] !== ' ') { out[out.length - 1] += ch; latin = false; continue; }
      if (OPEN.indexOf(ch) > -1) { pre += ch; latin = false; continue; }
      if (!CJK.test(ch) && latin) { out[out.length - 1] += ch; continue; }
      out.push(pre + ch);
      pre = '';
      latin = !CJK.test(ch);
    }
    if (pre) { out.push(pre); }
    return out;
  };
  if ('IntersectionObserver' in window && !still()) {
    var fold = window.innerHeight;
    var below = function (el) { return el.getBoundingClientRect().top + window.pageYOffset > fold; };
    var targets = [];
    doc.querySelectorAll('main .head h2, main .split h2, main .trade h2, main .worn h2, main .pearl-sec h2, main .cat-head h1').forEach(function (h) {
      if (h.children.length || !below(h)) { return; }
      var n = 0;
      var parts = pieces(h.textContent.trim());
      h.textContent = '';
      parts.forEach(function (w) {
        if (w === ' ') { h.appendChild(doc.createTextNode(' ')); return; }
        var sp = doc.createElement('span');
        sp.className = 'w';
        sp.style.setProperty('--i', n);
        sp.textContent = w;
        h.appendChild(sp);
        n += 1;
      });
      h.classList.add('rv-words');
      targets.push(h);
    });
    var sel = ['main .head p', 'main .head .btns', 'main .after', 'main .grid > .card', 'main .tiles > .tile',
      'main .pearls > a', 'main .look', 'main .look-note', 'main .services > div', 'main .values > div', 'main .ways li',
      'main .steps li', 'main .certs figure', 'main .gallery figure', 'main .timeline li', 'main .points li',
      'main .faq details', 'main .paths > div', 'main .teams li', 'main .split .copy > *', 'main .split .media',
      'main .trade > div > *', 'main .trade > img', 'main .worn > *', 'main .cols > *', 'main .pearl-sec .facts li',
      'main .contact-grid > *', 'main .cat-head > *', 'main .filters', 'main .pd', '.site-footer .foot > div'].join(',');
    var rows = new Map();
    doc.querySelectorAll(sel).forEach(function (el) {
      if (el.classList.contains('rv-words') || !below(el) || el.closest('.rv')) { return; }
      var key = el.parentNode;
      var top = Math.round(el.getBoundingClientRect().top);
      var row = rows.get(key);
      if (!row || row.top !== top) { row = { top: top, n: 0 }; rows.set(key, row); }
      var extra = el.matches('.head p') ? 0.15 : el.matches('.head .btns') ? 0.3 : 0;
      el.style.setProperty('--d', (Math.min(row.n, 5) * 0.1 + extra).toFixed(2) + 's');
      row.n += 1;
      el.classList.add('rv');
      targets.push(el);
    });
    var done = function (el) {
      el.classList.remove('rv', 'in', 'rv-words');
      el.style.removeProperty('--d');
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { return; }
        var el = en.target;
        io.unobserve(el);
        el.classList.add('in');
        var wait = 1300 + parseFloat(getComputedStyle(el).getPropertyValue('--d') || '0') * 1000 +
          (el.classList.contains('rv-words') ? el.querySelectorAll('.w').length * STEP : 0);
        setTimeout(function () { done(el); }, wait);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    targets.forEach(function (el) { io.observe(el); });
  }

  // Mobile drawer
  var drawer = doc.getElementById('drawer');
  var openBtn = doc.querySelector('.menu-btn');
  if (drawer && openBtn) {
    var closeBtn = drawer.querySelector('.drawer-close');
    var setOpen = function (open) {
      drawer.classList.toggle('open', open);
      drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
      openBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      doc.body.classList.toggle('locked', open);
      if (open) { setTimeout(function () { closeBtn.focus(); }, 80); } else { openBtn.focus(); }
    };
    openBtn.addEventListener('click', function () { setOpen(true); });
    closeBtn.addEventListener('click', function () { setOpen(false); });
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) { setOpen(false); }
    });
  }

  // Jewellery dropdown (click/keyboard; hover handled in CSS)
  doc.querySelectorAll('.has-mega').forEach(function (item) {
    var btn = item.querySelector('button');
    btn.addEventListener('click', function () {
      var open = !item.classList.contains('open');
      item.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    item.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { item.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); btn.focus(); }
    });
    doc.addEventListener('click', function (e) {
      if (!item.contains(e.target)) { item.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); }
    });
  });

  // Product gallery
  var main = doc.getElementById('gal-main');
  if (main) {
    var thumbs = doc.querySelectorAll('.thumbs button');
    thumbs.forEach(function (b) {
      b.addEventListener('click', function () {
        main.src = b.dataset.src;
        main.alt = b.dataset.alt;
        thumbs.forEach(function (x) { x.removeAttribute('aria-current'); });
        b.setAttribute('aria-current', 'true');
      });
    });
  }

  // Pearl filters on listing pages
  var chips = doc.querySelectorAll('[data-filter]');
  if (chips.length) {
    var cards = doc.querySelectorAll('.grid .card');
    var shown = doc.getElementById('shown');
    var apply = function (key) {
      var n = 0;
      cards.forEach(function (c) {
        var ok = key === 'all' || (' ' + c.dataset.pearls + ' ').indexOf(' ' + key + ' ') > -1;
        c.hidden = !ok;
        if (ok) { n++; }
      });
      chips.forEach(function (x) { x.setAttribute('aria-pressed', x.dataset.filter === key ? 'true' : 'false'); });
      if (shown) { shown.textContent = '共 ' + n + ' 件'; }
    };
    chips.forEach(function (c) { c.addEventListener('click', function () { apply(c.dataset.filter); }); });
  }

  // Enquiry prefill on the contact page: /contact?item=33168
  var asking = doc.getElementById('asking');
  if (asking) {
    var m = /[?&]item=(\d{5})\b/.exec(location.search);
    if (m) {
      var names = JSON.parse(asking.dataset.names || '{}');
      var label = names[m[1]] ? names[m[1]] + '（货号 ' + m[1] + '）' : '货号 ' + m[1] + ' 的作品';
      asking.querySelector('b').textContent = label;
      asking.classList.add('show');
    }
  }
})();
