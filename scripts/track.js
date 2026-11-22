// Contact-click measurement for Google Tag Manager (container GTM-5KD9B98P).
// Pushes one dataLayer event per click on a call, LINE, directions or map link:
//   { event: "contact_click", contact_method: "call" | "line" | "directions" | "map",
//     link_url, link_section, link_service }  (link_service: service card id or service page slug)
// GTM turns these into GA4 events and Google Ads conversions. No personal data is sent.
(function () {
  "use strict";

  function classify(link) {
    var href = link.getAttribute("href") || "";
    var text = (link.textContent || "").replace(/\s+/g, " ");
    if (/^tel:/i.test(href)) return "call";
    if (/^https?:\/\/(?:[\w-]+\.)*line\.me\//i.test(href)) return "line";
    if (/google\.[^/]+\/maps\/dir\//i.test(href)) return "directions";
    if (/(?:maps\.google\.|google\.[^/]+\/maps)/i.test(href)) {
      return text.indexOf("นำทาง") !== -1 ? "directions" : "map";
    }
    return "";
  }

  function sectionOf(link) {
    var node = link.closest("section[id], header, footer, dialog[id]");
    if (!node) return "";
    return node.id || node.tagName.toLowerCase();
  }

  // Which service the click is about: the homepage service card, else the service page slug.
  function serviceOf(link) {
    var card = link.closest("article.service-card[id]");
    if (card) return card.id;
    var path = typeof location !== "undefined" ? location.pathname : "";
    var m = /^\/([a-z-]+)\/$/.exec(path || "");
    return m ? m[1] : "";
  }

  function onClick(event) {
    var target = event.target;
    var link = target && target.closest ? target.closest("a[href]") : null;
    if (!link) return;
    var method = classify(link);
    if (!method) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: "contact_click",
      contact_method: method,
      link_url: link.href,
      link_section: sectionOf(link),
      link_service: serviceOf(link)
    });
  }

  // Capture phase so the push happens before navigation (tel: links leave the page).
  document.addEventListener("click", onClick, true);

  window.NualTrack = { classify: classify };
})();
