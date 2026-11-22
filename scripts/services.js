/* Progressive enhancement only: prices and booking links work without JS. */
(function () {
  "use strict";
  var motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (motion.matches || !("IntersectionObserver" in window)) return;

  var cards = document.querySelectorAll("#menu .service-card");
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-entering");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.08 });
  cards.forEach(function (card) { observer.observe(card); });
  function disableMotion(event) {
    if (!event.matches) return;
    observer.disconnect();
    cards.forEach(function (card) { card.classList.remove("is-entering"); });
  }
  if (motion.addEventListener) motion.addEventListener("change", disableMotion);
})();

/* Photo card arrows. Without JS the photos still scroll by swipe or trackpad. */
(function () {
  "use strict";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  document.querySelectorAll("[data-service-gallery]").forEach(function (gallery) {
    var track = gallery.querySelector(".service-gallery-track");
    var prev = gallery.querySelector(".service-gallery-prev");
    var next = gallery.querySelector(".service-gallery-next");
    var count = gallery.querySelector(".service-gallery-count");
    var total = track ? track.children.length : 0;
    if (!track || !prev || !next || total < 2) return;

    function index() { return Math.round(track.scrollLeft / Math.max(track.clientWidth, 1)); }
    function update() {
      var i = Math.min(Math.max(index(), 0), total - 1);
      prev.disabled = i === 0;
      next.disabled = i === total - 1;
      if (count) count.textContent = (i + 1) + " / " + total;
    }
    function go(step) {
      var target = Math.min(Math.max(index() + step, 0), total - 1);
      track.scrollTo({ left: target * track.clientWidth, behavior: reduce && reduce.matches ? "auto" : "smooth" });
    }
    prev.hidden = false;
    next.hidden = false;
    prev.addEventListener("click", function () { go(-1); });
    next.addEventListener("click", function () { go(1); });
    track.addEventListener("keydown", function (event) {
      if (event.key === "ArrowLeft") { event.preventDefault(); go(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); go(1); }
    });
    var pending = false;
    track.addEventListener("scroll", function () {
      if (pending) return;
      pending = true;
      window.requestAnimationFrame(function () { pending = false; update(); });
    }, { passive: true });
    window.addEventListener("resize", update);
    update();
  });
})();
