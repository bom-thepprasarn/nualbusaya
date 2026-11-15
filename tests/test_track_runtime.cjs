// Runtime checks for scripts/track.js: link classification and dataLayer pushes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../scripts/track.js'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, '../index.html'), 'utf8');

let clickHandler;
const document = { addEventListener(name, fn, capture) {
  assert.equal(name, 'click'); assert.equal(capture, true); clickHandler = fn; } };
const window = {};
vm.runInNewContext(source, { document, window });

function link(href, text = '', section = 'contact') {
  return {
    href, textContent: text,
    getAttribute(name) { return name === 'href' ? href : null; },
    closest(sel) {
      if (sel === 'a[href]') return this;
      return { id: section, tagName: 'SECTION' };
    },
  };
}

const { classify } = window.NualTrack;
assert.equal(classify(link('tel:+66967781585')), 'call');
assert.equal(classify(link('https://line.me/R/ti/p/@288ojpuq')), 'line');
assert.equal(classify(link('https://www.google.com/maps/dir/?api=1&destination=13.9320524,100.7484876')), 'directions');
assert.equal(classify(link('https://maps.google.com/?cid=15830764363691679197', ' นำทาง ')), 'directions');
assert.equal(classify(link('https://maps.google.com/?cid=15830764363691679197', 'อ่านรีวิวทั้งหมดบน Google')), 'map');
assert.equal(classify(link('https://www.tiktok.com/@nual.busaya')), '');
assert.equal(classify(link('#menu')), '');

// A click on a child element of a tracked link pushes exactly one event.
const a = link('tel:+66967781585', 'โทร', 'top');
clickHandler({ target: { closest: () => a } });
assert.deepEqual(JSON.parse(JSON.stringify(window.dataLayer)), [{
  event: 'contact_click', contact_method: 'call', link_url: 'tel:+66967781585', link_section: 'top' }]);
clickHandler({ target: { closest: () => null } });
clickHandler({ target: { closest: () => link('#menu') } });
assert.equal(window.dataLayer.length, 1, 'untracked clicks must not push');

// Every contact link on the page maps to a conversion method.
const hrefs = [...html.matchAll(/<a\b[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/g)];
const counts = {};
for (const [, href, inner] of hrefs) {
  const m = classify(link(href.replace(/&amp;/g, '&'), inner.replace(/<[^>]+>/g, ' ')));
  if (m) counts[m] = (counts[m] || 0) + 1;
}
assert.ok(counts.call >= 1 && counts.line >= 1 && counts.directions >= 2 && counts.map >= 1, JSON.stringify(counts));
console.log('track runtime ok', JSON.stringify(counts));
