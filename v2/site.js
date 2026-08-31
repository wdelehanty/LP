/* Steel and Signal interaction layer. Everything here is progressive
   enhancement: no JS, no motion, full content. Reduced-motion gets the
   static site. */
(function () {
  var doc = document.documentElement;
  doc.classList.add('js');
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (still) { doc.classList.add('still'); return; }

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

  /* Scroll-triggered reveals, fast and once */
  var targets = document.querySelectorAll(
    '.section-head, .row, .index-row, .band, .stack-short, .offhours .copy, ' +
    '.cs-main > h2, .cs-aside .note, .cs-visual figure, .lab-entry, ' +
    '.principle, .stack-group, .changelog-entry, .about-hero .grid, .photo-block'
  );
  targets.forEach(function (el) { el.classList.add('reveal'); });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  targets.forEach(function (el) { io.observe(el); });

  /* Scroll progress, a signal thread across the top */
  var bar = document.createElement('div');
  bar.id = 'progress';
  document.body.appendChild(bar);

  /* Slow drift on the hero backdrop */
  var hero = document.querySelector('.hero, .cs-header');
  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var max = doc.scrollHeight - window.innerHeight;
      bar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
      if (hero) hero.style.setProperty('--drift', Math.min(window.scrollY * 0.12, 80) + 'px');
      ticking = false;
    });
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();
