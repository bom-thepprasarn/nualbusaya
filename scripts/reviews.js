(function () {
  "use strict";
  var card = document.querySelector(".review-summary-card");
  if (!card) return;
  var verified = document.getElementById("review-verified-data");
  var neutral = document.getElementById("review-neutral");
  var score = document.getElementById("rv-score");
  var stars = document.getElementById("rv-stars");
  var count = document.getElementById("rv-count");
  var checked = document.getElementById("review-checked");
  var starPath = "m12 2.5 2.94 5.96 6.58.95-4.76 4.64 1.12 6.55L12 17.51l-5.88 3.09 1.12-6.55L2.48 9.41l6.58-.95z";
  var ns = "http://www.w3.org/2000/svg";

  function render(data) {
    var rating = data && data.rating;
    var date = data && data.verifiedAt && new Date(data.verifiedAt);
    var valid = !!data && data.verified === true && typeof rating === "number" &&
      Number.isFinite(rating) && rating > 0 && rating <= 5 && date && Number.isFinite(date.getTime());
    verified.hidden = !valid;
    neutral.hidden = !!valid;
    stars.replaceChildren();
    if (!valid) {
      score.textContent = "";
      count.textContent = "";
      checked.textContent = "";
      stars.removeAttribute("aria-label");
      return;
    }
    var displayRating = rating === 5 ? "5.0" : String(Math.min(4.99, Math.round(rating * 100) / 100));
    score.textContent = displayRating;
    score.hidden = false;
    stars.hidden = false;
    stars.setAttribute("aria-label", displayRating + " จาก 5 ดาว");
    for (var i = 0; i < 5; i++) {
      var svg = document.createElementNS(ns, "svg");
      svg.setAttribute("viewBox", "0 0 24 24");
      svg.setAttribute("aria-hidden", "true");
      svg.setAttribute("focusable", "false");
      var empty = document.createElementNS(ns, "path");
      empty.setAttribute("d", starPath);
      empty.setAttribute("class", "review-star-empty");
      var fill = document.createElementNS(ns, "path");
      fill.setAttribute("d", starPath);
      fill.setAttribute("class", "review-star-fill");
      var fraction = Math.max(0, Math.min(1, rating - i));
      fill.style.clipPath = "inset(0 " + ((1 - fraction) * 100) + "% 0 0)";
      svg.appendChild(empty);
      svg.appendChild(fill);
      stars.appendChild(svg);
    }
    var validCount = Number.isInteger(data.count) && data.count > 0;
    count.hidden = !validCount;
    count.textContent = validCount ? "จาก " + data.count.toLocaleString("th-TH") + " รีวิว" : "";
    checked.textContent = "ตรวจสอบล่าสุดเมื่อ " +
      new Intl.DateTimeFormat("th-TH", { day:"numeric", month:"short", year:"numeric", timeZone:"Asia/Bangkok" }).format(date);
  }

  window.NUAL_REVIEW_SUMMARY = { update:render };
  render({
    verified:card.hasAttribute("data-verified-rating"),
    rating:Number(card.dataset.verifiedRating),
    count:Number(card.dataset.reviewCount),
    verifiedAt:card.dataset.verifiedDate ? card.dataset.verifiedDate + "T00:00:00+07:00" : null,
    source:"snapshot"
  });

  // Native scroll-snap works without a library, cloning, or autoplay.
  var track = document.getElementById("rv-grid");
  var slides = track.querySelectorAll(".curated-review-card");
  var previous = document.getElementById("review-prev");
  var next = document.getElementById("review-next");
  var position = document.getElementById("review-position");
  var motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  function updateControls() {
    var end = track.scrollWidth - track.clientWidth;
    previous.disabled = track.scrollLeft <= 3;
    next.disabled = track.scrollLeft >= end - 3;
    var left = track.getBoundingClientRect().left;
    var visible = [];
    slides.forEach(function (slide,index) {
      var box = slide.getBoundingClientRect();
      if (box.left < left + track.clientWidth - 20 && box.right > left + 20) visible.push(index+1);
    });
    if (visible.length) position.textContent = "รีวิว " + visible[0] + (visible.length>1 ? "–"+visible[visible.length-1] : "") + " จาก " + slides.length;
  }
  function step(direction) {
    var gap = parseFloat(window.getComputedStyle(track).gap) || 0;
    var distance = slides[0].getBoundingClientRect().width + gap;
    track.scrollBy({left:direction*distance,behavior:motion.matches ? "auto" : "smooth"});
  }
  previous.addEventListener("click",function () { step(-1); });
  next.addEventListener("click",function () { step(1); });
  track.addEventListener("scroll",updateControls,{passive:true});
  track.addEventListener("keydown",function (event) {
    if (event.target !== track) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();step(event.key === "ArrowRight" ? 1 : -1);
    }
  });
  window.addEventListener("resize",updateControls);
  if ("ResizeObserver" in window) new ResizeObserver(updateControls).observe(track);
  updateControls();

  if (motion.matches || !("IntersectionObserver" in window)) return;
  var cards = document.querySelectorAll(".review-summary-card, .curated-review-card");
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-entering");
      observer.unobserve(entry.target);
    });
  }, { threshold:0.15 });
  cards.forEach(function (item) { observer.observe(item); });
  if (motion.addEventListener) motion.addEventListener("change", function (event) {
    if (event.matches) { observer.disconnect();cards.forEach(function (item) { item.classList.remove("is-entering"); }); }
  });
})();
