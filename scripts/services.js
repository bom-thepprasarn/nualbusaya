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
