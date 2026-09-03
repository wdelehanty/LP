/* Steel and Signal interaction layer. Everything here is progressive
   enhancement: no JS, no motion, full content. Reduced-motion gets the
   static site, with the status rail still updating in place.

   Motion budget (Brief 6): scroll reveal once per element, three hover
   effects in CSS, and the rail tick and dot pulse as the only ambient
   motion. Nothing else. */
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) doc.classList.add('still');

  /* Count a number up in place. Keeps whatever sits around the digits
     ("$", "~", "M+", "K") and the decimal precision of the original. */
  function countUp(el, to, ms) {
    var text = el.textContent;
    var m = /-?\d[\d,]*(\.\d+)?/.exec(text);
    if (!m) { return; }
    var pre = text.slice(0, m.index);
    var post = text.slice(m.index + m[0].length);
    var decimals = m[1] ? m[1].length - 1 : 0;
    if (to == null) to = parseFloat(m[0].replace(/,/g, ''));
    if (isNaN(to)) { return; }
    var done = pre + to.toFixed(decimals) + post;
    if (still || !window.requestAnimationFrame) { el.textContent = done; return; }
    /* Start at 85% of the final value so no frame ever reads as a wrong
       number. The tilde, the plus, and the units never move. */
    var from = to * 0.85;
    var start = null;
    el.textContent = pre + from.toFixed(decimals) + post;
    function frame(now) {
      if (start === null) start = now;
      var t = Math.min(1, (now - start) / ms);
      var e = 1 - Math.pow(1 - t, 3);
      el.textContent = pre + (from + (to - from) * e).toFixed(decimals) + post;
      if (t < 1) requestAnimationFrame(frame); else el.textContent = done;
    }
    requestAnimationFrame(frame);
  }

  /* Status rail: baked values are already in the markup, so the strip is
     never empty. Numbers tick in on first paint, then the Worker at
     data-status may replace them. Any failure leaves the baked values. */
  var rail = document.querySelector('.rail');
  if (rail) {
    rail.querySelectorAll('[data-rail][data-count]').forEach(function (b) { countUp(b, null, 400); });
    var src = rail.getAttribute('data-status');
    if (src && window.fetch) {
      fetch(src, { cache: 'default' })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (s) {
          if (!s) return;
          rail.querySelectorAll('[data-rail]').forEach(function (b) {
            var v = s[b.getAttribute('data-rail')];
            if (v == null) return;
            if (typeof v === 'number') {
              if (parseFloat(b.textContent) !== v) countUp(b, v, 400);
            } else {
              b.textContent = String(v);
            }
          });
        })
        .catch(function () {});
    }
  }

  /* About carousel: CSS does the scrolling and snapping; this adds the
     buttons, the dots, and arrow keys. Reduced motion makes it instant. */
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.track');
    var slides = track.querySelectorAll('.slide');
    var dots = car.querySelector('.dots');
    var section = car.closest('section');
    var buttons = section ? section.querySelectorAll('.car-btn') : [];
    if (!slides.length) return;
    var current = 0;
    function step() { return slides.length > 1 ? slides[1].offsetLeft - slides[0].offsetLeft : slides[0].offsetWidth; }
    function index() { return Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / step()))); }
    function go(i) {
      current = Math.max(0, Math.min(slides.length - 1, i));
      track.scrollTo({ left: slides[current].offsetLeft, behavior: still ? 'auto' : 'smooth' });
      mark(current);
    }
    var dotEls = [];
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Photo ' + (i + 1));
      b.tabIndex = -1;  /* the dots sit under aria-hidden; the buttons and arrow keys carry the keyboard path */
      b.addEventListener('click', function () { go(i); });
      dots.appendChild(b);
      dotEls.push(b);
    });
    function mark(i) {
      dotEls.forEach(function (b, j) {
        if (j === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
      });
    }
    function sync() { current = index(); mark(current); }
    var timer = null;
    track.addEventListener('scroll', function () {
      if (timer) return;
      timer = setTimeout(function () { timer = null; sync(); }, 80);
    }, { passive: true });
    sync();
    Array.prototype.forEach.call(buttons, function (b) {
      b.addEventListener('click', function () { go(current + Number(b.getAttribute('data-dir'))); });
    });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(current + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(current - 1); }
    });
  });

  // Proof model. Direct-booked = budget * (275 / 72) after the funnel rebuild,
  // divided by 2.5 before it. Both ratios are inventory numbers; nothing else.
  var model = document.getElementById('paid-model');
  if (model) {
    var range = model.querySelector('input[type="range"]');
    var budgetOut = model.querySelector('output');
    var val = model.querySelector('.val');
    var segs = model.querySelectorAll('.seg button');
    var mode = 'after', shown = 0, tweenId = null, settle = null;
    function money(n) {
      if (n >= 1e6) return '$' + (n / 1e6).toFixed(2).replace(/\.?0+$/, '') + 'M';
      return '$' + Math.round(n / 1000) + 'K';
    }
    function target() {
      var after = Number(range.value) * 275 / 72;
      return mode === 'after' ? after : after / 2.5;
    }
    function show(n) { shown = n; val.textContent = money(n); }
    function update() {
      var b = money(Number(range.value));
      budgetOut.textContent = b;
      range.setAttribute('aria-valuetext', b);
      var to = target();
      if (still) { show(to); return; }
      if (tweenId) cancelAnimationFrame(tweenId);
      clearTimeout(settle);
      var from = shown, t0 = performance.now();
      tweenId = requestAnimationFrame(function frame(now) {
        var p = Math.min(1, (now - t0) / 150);
        show(from + (to - from) * p);
        tweenId = p < 1 ? requestAnimationFrame(frame) : null;
      });
      // Throttled frames (background tab) still land on the final value.
      settle = setTimeout(function () { if (tweenId) { cancelAnimationFrame(tweenId); tweenId = null; } show(to); }, 200);
    }
    range.addEventListener('input', update);
    Array.prototype.forEach.call(segs, function (b) {
      b.addEventListener('click', function () {
        mode = b.getAttribute('data-mode');
        Array.prototype.forEach.call(segs, function (o) { o.setAttribute('aria-pressed', String(o === b)); });
        update();
      });
    });
    budgetOut.textContent = money(Number(range.value));
    show(target());
  }

  // Demo call. Native audio behind custom controls; the transcript follows
  // currentTime, and the report card beside it gets the booking once, on end.
  Array.prototype.forEach.call(document.querySelectorAll('[data-demo]'), function (demo) {
    var audio = demo.querySelector('audio'), play = demo.querySelector('.play');
    var bar = demo.querySelector('.bar'), fill = demo.querySelector('.fill');
    var cur = demo.querySelector('.cur'), durEl = demo.querySelector('.dur');
    var list = demo.querySelector('.transcript'), lines = list.querySelectorAll('li');
    var rows = demo.querySelector('.rows'), booking = demo.querySelector('[data-booking]');
    var booked = demo.querySelector('[data-booked]');
    var active = -1, done = false;
    if (!audio || !play) return;
    function fmt(s) { s = Math.max(0, Math.round(s || 0)); return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2); }
    function dur() { return isFinite(audio.duration) && audio.duration > 0 ? audio.duration : Number(bar.getAttribute('aria-valuemax')); }
    function keep(li) {
      var top = li.offsetTop, view = list.clientHeight;
      if (top < list.scrollTop + 8 || top + li.offsetHeight > list.scrollTop + view - 8) {
        list.scrollTo({ top: Math.max(0, top - view * 0.3), behavior: 'smooth' });
      }
    }
    function paint() {
      var d = dur(), t = audio.currentTime || 0;
      fill.style.width = (d ? Math.min(100, t / d * 100) : 0) + '%';
      cur.textContent = fmt(t);
      bar.setAttribute('aria-valuenow', Math.round(t));
      bar.setAttribute('aria-valuetext', fmt(t) + ' of ' + fmt(d));
      var i = -1;
      Array.prototype.forEach.call(lines, function (li, j) { if (t >= Number(li.getAttribute('data-t')) - 0.05) i = j; });
      if (i !== active) {
        active = i;
        Array.prototype.forEach.call(lines, function (li, j) { li.classList.toggle('on', j === i); });
        if (i >= 0 && !still) keep(lines[i]);
      }
    }
    function state(playing) {
      play.setAttribute('aria-pressed', String(playing));
      play.setAttribute('aria-label', playing ? 'Pause the demo call' : 'Play the demo call');
    }
    function seek(t) { audio.currentTime = Math.max(0, Math.min(dur(), t)); paint(); }
    play.addEventListener('click', function () { if (audio.paused) audio.play(); else audio.pause(); });
    audio.addEventListener('play', function () { state(true); });
    audio.addEventListener('pause', function () { state(false); });
    audio.addEventListener('loadedmetadata', function () { durEl.textContent = fmt(audio.duration); bar.setAttribute('aria-valuemax', Math.round(audio.duration)); paint(); });
    audio.addEventListener('timeupdate', paint);
    audio.addEventListener('ended', function () {
      state(false); paint();
      if (done) return;
      done = true;
      if (rows && booking) rows.appendChild(booking.content.cloneNode(true));
      if (booked) { booked.textContent = String(Number(booked.textContent) + 1); booked.classList.add('bump'); }
    });
    bar.addEventListener('click', function (e) {
      var r = bar.getBoundingClientRect();
      seek((e.clientX - r.left) / r.width * dur());
    });
    bar.addEventListener('keydown', function (e) {
      var t = audio.currentTime || 0;
      if (e.key === 'ArrowRight' || e.key === 'ArrowUp') { seek(t + 5); e.preventDefault(); }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') { seek(t - 5); e.preventDefault(); }
      else if (e.key === 'Home') { seek(0); e.preventDefault(); }
      else if (e.key === 'End') { seek(dur()); e.preventDefault(); }
      else if (e.key === ' ' || e.key === 'Enter') { play.click(); e.preventDefault(); }
    });
    paint();
  });

  // Screen-recording loops, one per page, inside a photo frame. Mounted only
  // when motion is allowed and the viewport is at least 768 wide; the still
  // stays put otherwise, and comes back if neither encoding loads.
  if (!still && window.matchMedia('(min-width: 768px)').matches) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-loop]'), function (frame) {
      var img = frame.querySelector('img'), base = frame.getAttribute('data-loop');
      if (!img || !base) return;
      var v = document.createElement('video');
      v.autoplay = true; v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'metadata';
      v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
      v.setAttribute('aria-label', frame.getAttribute('data-loop-label') || img.alt);
      v.poster = img.currentSrc || img.src;
      v.width = img.width; v.height = img.height;
      [['webm', 'video/webm'], ['mp4', 'video/mp4']].forEach(function (t) {
        var src = document.createElement('source'); src.src = base + '.' + t[0]; src.type = t[1]; v.appendChild(src);
      });
      v.addEventListener('error', function () {
        if (v.networkState === 3) { v.remove(); img.style.display = ''; }
      }, true);
      img.style.display = 'none';
      frame.appendChild(v);
    });
  }

  if (still) return;

  /* Kinetic headline: split display headings into words, stagger the rise */
  document.querySelectorAll('.hero h1, .cs-header h1').forEach(function (h) {
    var i = 0;
    function split(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var w = document.createElement('span');
            w.className = 'kw';
            w.style.setProperty('--i', i++);
            w.textContent = part;
            frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          split(child);
        }
      });
    }
    split(h);
    h.classList.add('kinetic');
  });

  /* Scroll-triggered reveals: 12px rise, 400ms, once per element */
  var targets = document.querySelectorAll(
    '.section-head, .row, .index-row, .band, .stack-short, .rows-note, ' +
    '.strip figure, .offhours .copy, .offhours .shot, ' +
    '.cs-main > h2, .built, .cs-aside .note, .cs-visual figure, .lab-entry, ' +
    '.principle, .stack-group, .changelog-entry, .photo-block'
  );
  targets.forEach(function (el) { el.classList.add('reveal'); });
  document.querySelectorAll('.strip figure').forEach(function (el, i) {
    el.style.transitionDelay = (i * 60) + 'ms';
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  targets.forEach(function (el) { io.observe(el); });

  /* Proof numerals count up once when the band comes into view */
  var band = document.querySelector('.band');
  if (band) {
    var bio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        bio.unobserve(e.target);
        e.target.querySelectorAll('.figure[data-count]').forEach(function (f) { countUp(f, null, 500); });
      });
    }, { threshold: 0.3 });
    bio.observe(band);
  }

  /* Safety sweep: observers and transitions can stall in throttled
     windows, and fast scrolling can leave elements unrevealed above the
     viewport. Nothing is allowed to stay hidden. */
  function forceIn(el) {
    el.style.transition = 'none';
    el.classList.add('in');
    io.unobserve(el);
  }
  var sweep = setInterval(function () {
    var pending = document.querySelectorAll('.reveal:not(.in)');
    if (!pending.length) { clearInterval(sweep); return; }
    pending.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.bottom < 0 || r.top < window.innerHeight * 1.15) forceIn(el);
    });
  }, 600);
  setTimeout(function () {
    document.querySelectorAll('.reveal:not(.in)').forEach(forceIn);
    clearInterval(sweep);
  }, 6000);
})();
