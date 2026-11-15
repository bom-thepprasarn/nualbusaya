const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../scripts/outcall.js'), 'utf8');

function setup(storage = new Map()) {
  let now = 0, nextId = 0;
  const tasks = new Map(), docEvents = {};
  function element(open = false) {
    return { open, events: {}, addEventListener(name, fn) { this.events[name] = fn; },
      close() { this.open = false; this.events.close?.(); },
      showModal() { this.open = true; this.shown = (this.shown || 0) + 1; }, focus() {} };
  }
  const first = element(true), dialog = element(), close = element();
  const document = { visibilityState: 'visible', activeElement: null, body: {},
    getElementById(id) { return ({'website-offer':first,'outcall-dialog':dialog,'outcall-close':close})[id]; },
    querySelector() { return first.open || dialog.open ? {} : null; },
    addEventListener(name, fn) { docEvents[name] = fn; } };
  const window = { setTimeout(fn, delay) { const id = ++nextId;tasks.set(id,{fn,due:now+delay});return id; }, clearTimeout(id) { tasks.delete(id); } };
  const sessionStorage = { getItem(key) { return storage.get(key) ?? null; }, setItem(key,value) { storage.set(key,value); } };
  vm.runInNewContext(source,{document,window,sessionStorage,Date:{now:()=>now}});
  function advance(ms) { now+=ms;for(const [id,task] of [...tasks]) if(task.due<=now){tasks.delete(id);task.fn();} }
  return {first,dialog,close,document,storage,advance,visible() { document.visibilityState='visible';docEvents.visibilitychange(); }};
}

const a = setup();
a.advance(120000);assert.equal(a.dialog.open,false,'second popup must not precede first close');
a.first.close();a.advance(59999);assert.equal(a.dialog.open,false,'must wait a full minute');
a.advance(1);assert.equal(a.dialog.open,true);assert.equal(a.first.open,false);
a.close.events.click();assert.equal(a.dialog.open,false);
a.first.open=true;a.first.close();a.advance(120000);assert.equal(a.dialog.shown,1,'show once per tab session');
const b = setup();b.first.close();b.document.visibilityState='hidden';b.advance(60000);
assert.equal(b.dialog.open,false,'do not interrupt a background visitor');
b.visible();assert.equal(b.dialog.open,true,'show when the visitor returns after due time');
const c = setup(a.storage);c.first.close();c.advance(120000);assert.equal(c.dialog.open,false,'reload preserves once-per-session status');
console.log('PASS: first-close ordering, full 60-second delay, no overlap, close action, once/session, background deferral, reload persistence');
