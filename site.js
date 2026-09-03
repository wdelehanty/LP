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
