import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {mountDelivery} from '../web/delivery.mjs';

function fixture(values, width=640) {
  const dom=new JSDOM('<div id="history"></div>',{pretendToBeVisual:true});
  const root=dom.window.document.getElementById('history');
  let resize,disconnected=false;
  dom.window.ResizeObserver=class {
    constructor(callback){resize=callback;}
    observe(){}
    disconnect(){disconnected=true;}
  };
  root.getBoundingClientRect=()=>({width});
  const record={project:{id:'standard'},items:[],history:{coverage:'Pinned observations only.',comparisons:[],snapshots:values.map((value,i)=>({observedOn:'2026-10-30',source:{sha256:String(i).padStart(64,'a')},metrics:{work:{done:value===null?0:value,total:value===null?0:100,percent:value},ledger:{done:i,total:100,percent:i}}}))}};
  const mounted=mountDelivery(root,record);
  return {dom,root,record,mounted,resizeTo(value){width=value;resize();},disconnected:()=>disconnected,change(selector,value){const input=root.querySelector(selector);input.value=String(value);input.dispatchEvent(new dom.window.Event('change',{bubbles:true}));}};
}

test('dense same-day history retains every mark and exact row without repeated axis/value labels',()=>{
  const f=fixture(Array.from({length:40},(_,i)=>i*2));
  assert.equal(f.root.querySelectorAll('circle').length,40);
  assert.equal(f.root.querySelectorAll('tbody tr').length,40);
  assert.equal(f.root.querySelectorAll('.pd-end-label').length,1);
  assert.equal(f.root.querySelectorAll('svg text').length,8);
  assert.match(f.root.querySelector('figcaption').textContent,/does not represent elapsed time/);
  assert.match(f.root.querySelector('.pd-observation').textContent,/78.0%/);
  assert.match(f.root.querySelector('svg').getAttribute('aria-label'),/equally spaced/);
});

test('observation selection preserves keyboard focus and exposes fraction, date and percentage',()=>{
  const f=fixture([20,40,80]);
  f.change('[data-history-observation]',0);
  assert.equal(f.dom.window.document.activeElement,f.root.querySelector('[data-history-observation]'));
  assert.match(f.root.querySelector('.pd-observation').textContent,/20.0%20\/100/);
  assert.match(f.root.querySelector('[data-history-observation] option:checked').textContent,/2026-10-30 · 20.0% · 20\/100/);
  assert.equal(f.root.querySelector('.pd-selected-point').getAttribute('cx'),'42');
});

test('unmeasured observations leave a real path gap and remain in the table',()=>{
  const f=fixture([10,null,30]);
  assert.equal(f.root.querySelectorAll('circle').length,2);
  assert.equal((f.root.querySelector('.pd-line').getAttribute('d').match(/M/g)||[]).length,2);
  assert.equal(f.root.querySelectorAll('tbody tr').length,3);
  f.change('[data-history-observation]',1);
  assert.match(f.root.querySelector('.pd-observation').textContent,/Not measured/);
  assert.equal(f.root.querySelectorAll('.pd-selected-point').length,0);
});

test('single zero-percent snapshot is measured and uses one observation tick',()=>{
  const f=fixture([0]);
  assert.equal(f.root.querySelectorAll('circle').length,1);
  assert.match(f.root.querySelector('.pd-observation').textContent,/0.0%/);
  assert.equal(f.root.querySelectorAll('svg text').length,6);
});

test('narrow layout reduces ticks instead of scaling a fixed desktop drawing; cleanup disconnects',()=>{
  const f=fixture(Array.from({length:50},(_,i)=>i),900);
  assert.equal(f.root.querySelector('svg').getAttribute('viewBox'),'0 0 900 246');
  assert.equal(f.root.querySelectorAll('svg text').length,10);
  f.resizeTo(280);
  assert.equal(f.root.querySelector('svg').getAttribute('viewBox'),'0 0 280 246');
  assert.equal(f.root.querySelectorAll('svg text').length,7);
  assert.equal(f.root.querySelectorAll('circle').length,50);
  f.mounted.destroy();
  assert.equal(f.disconnected(),true);
});

test('measure switch changes all displayed values and retains observation selection without source mutation',()=>{
  const f=fixture([40,60,80]);const before=JSON.stringify(f.record);
  f.change('[data-history-observation]',1);
  f.change('[data-delivery-measure]','ledger');
  assert.match(f.root.querySelector('.pd-observation').textContent,/1.0%1\/100 retained/);
  assert.equal(f.root.querySelector('[data-history-observation]').value,'1');
  assert.equal(f.dom.window.document.activeElement,f.root.querySelector('[data-delivery-measure]'));
  assert.equal(JSON.stringify(f.record),before);
});

test('empty or all-unknown history never draws a zero-progress series',()=>{
  for(const values of [[],[null,null]]){
    const f=fixture(values);
    assert.equal(f.root.querySelector('svg'),null);
    assert.match(f.root.textContent,/No measured denominator/);
    assert.equal(f.root.querySelectorAll('tbody tr').length,values.length);
  }
});
