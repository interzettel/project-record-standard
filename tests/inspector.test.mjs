import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {JSDOM} from 'jsdom';

const html = execFileSync('python3', ['-c', `
import json
from pathlib import Path
from project_record.inspector import inspector_model
from project_record.inspector_views import render_inspector
root=Path('tests/fixtures/inspector')
print(render_inspector(inspector_model(root,json.loads((root/'selection.json').read_text()),observed_at='2026-11-06T00:15:00+01:00')))
`], {encoding:'utf8', env:{...process.env,PYTHONPATH:'src'}, maxBuffer:8*1024*1024});

function page() {
  return new JSDOM(html, {url:'file:///owner-local/index.html', runScripts:'dangerously', pretendToBeVisual:true});
}

test('generated file filters only index, retaining focus, source targets and a mounted announcement', () => {
  const dom=page(), doc=dom.window.document;
  const input=doc.getElementById('find'), status=doc.getElementById('results');
  const artifacts=doc.querySelectorAll('.artifact').length;
  input.focus(); input.value='MISSING'; input.dispatchEvent(new dom.window.Event('input'));
  assert.equal(doc.activeElement,input);
  assert.equal(doc.getElementById('results'),status);
  assert.match(status.textContent,/1 matching declared files/);
  assert.equal([...doc.querySelectorAll('#artifact-index li')].filter(e=>!e.hidden).length,1);
  assert.equal(doc.querySelectorAll('.artifact').length,artifacts);
  input.value='not-a-real-file'; input.dispatchEvent(new dom.window.Event('input'));
  assert.match(status.textContent,/0 matching declared files/);
  assert.equal(doc.getElementById('artifact-REC-1').hidden,false);
  dom.window.close();
});

test('all source joins target unique rendered fields without external resources or data execution',()=>{
  const dom=page(), doc=dom.window.document;
  const ids=[...doc.querySelectorAll('[id]')].map(e=>e.id);
  assert.equal(new Set(ids).size,ids.length);
  for(const link of doc.querySelectorAll('a')){
    assert(link.getAttribute('href').startsWith('#'));
    assert(doc.getElementById(link.getAttribute('href').slice(1)));
  }
  assert.equal(doc.querySelectorAll('[src],link,iframe,object,form').length,0);
  assert.equal(doc.querySelectorAll('script').length,1);
  assert.equal(doc.querySelectorAll('script[src]').length,0);
  assert.equal(doc.querySelectorAll('input').length,1);
  assert.equal(doc.querySelector('input').getAttribute('type'),'search');
  assert(doc.querySelector('label[for="find"]'));
  dom.window.close();
});

test('static content and deep source fragment remain available with scripts disabled',()=>{
  const dom=new JSDOM(html,{url:'file:///owner-local/index.html#artifact-REC-1'}),doc=dom.window.document;
  assert.equal(dom.window.location.hash,'#artifact-REC-1');
  assert(doc.getElementById('artifact-REC-1'));
  assert.equal(doc.querySelectorAll('.artifact').length,8);
  assert.match(doc.querySelector('main').textContent,/Required leaves/);
  assert.match(doc.querySelector('main').textContent,/No source body available/);
  assert.match(doc.querySelector('main').textContent,/Uninterpreted/);
  assert.equal(doc.querySelectorAll('[hidden]').length,0);
  dom.window.close();
});
