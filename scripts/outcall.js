(function () {
  "use strict";
  var first = document.getElementById("website-offer");
  var dialog = document.getElementById("outcall-dialog");
  var close = document.getElementById("outcall-close");
  if (!first || !dialog || typeof dialog.showModal !== "function") return;
  var delay = 60000;
  var shownKey = "nualbusaya-outcall-shown-v1";
  var dueKey = "nualbusaya-outcall-due-v1";
  var firstKey = "nualbusaya-120min-100-offer-v1";
  var timer;
  var due = 0;
  var shown = false;
  var previousFocus;
  function read(key) { try { return sessionStorage.getItem(key); } catch (e) { return null; } }
  function write(key,value) { try { sessionStorage.setItem(key,value); } catch (e) {} }
  shown = read(shownKey) === "shown";
  function showIfReady() {
    if (shown || !due || Date.now() < due) return;
    if (document.visibilityState !== "visible" || document.querySelector("dialog[open]")) return;
    previousFocus = document.activeElement;
    dialog.showModal();
    shown = true;
    write(shownKey,"shown");
  }
  function scheduleAfterFirst() {
    if (shown) return;
    due = Date.now() + delay;
    write(dueKey,String(due));
    window.clearTimeout(timer);
    timer = window.setTimeout(showIfReady,delay);
  }
  first.addEventListener("close",scheduleAfterFirst);
  document.addEventListener("visibilitychange",showIfReady);
  close.addEventListener("click",function () { dialog.close(); });
  dialog.addEventListener("close",function () {
    if (previousFocus && previousFocus !== document.body && previousFocus.focus) previousFocus.focus();
  });
  if (!shown && read(firstKey) === "shown" && !first.open) {
    var saved = Number(read(dueKey));
    if (saved > 0) {
      due = saved;
      timer = window.setTimeout(showIfReady,Math.max(0,due-Date.now()));
    } else { scheduleAfterFirst(); }
  }
})();
