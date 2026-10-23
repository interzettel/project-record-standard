import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {mountExplorer} from '../web/components.mjs';

function fixture() {
  const dom=new JSDOM('<main><div id="work"></div></main>',{pretendToBeVisual:true});
  dom.window.HTMLElement.prototype.scrollIntoView=function(){};
  const root=dom.window.document.getElementById('work');
  const item=(id,state,dependsOn=[])=>({id,title:'Work '+id,groupId:'G',milestoneId:'M',state,sourceState:state,required:true,blocked:false,dependsOn,unmappedDependencies:[],evidence:[],criterion:'Verify '+id,owner:'Maintainer',priority:'P1',issueUrl:null,note:null,deferReason:null});
  mountExplorer(root,{groups:[{id:'G',title:'Deliverable'}],milestones:[{id:'M',title:'Outcome'}],items:[item('A','active',['B']),item('B','done')]});
  const change=(selector,value,type='change')=>{const el=root.querySelector(selector);el.value=value;el.dispatchEvent(new dom.window.Event(type,{bubbles:true}));return el;};
  return {dom,root,change};
}

test('filter updates preserve one mounted result announcement node',()=>{
  const {dom,root,change}=fixture();
  const status=root.querySelector('[role="status"]');
  const observer=new dom.window.MutationObserver(()=>{});
  observer.observe(root,{childList:true,subtree:true});
  change('[data-pr-search]','Work A','input');
  assert.equal(root.querySelector('[role="status"]'),status);
  assert.match(status.textContent,/1 matching items/);
  change('[data-pr-state]','done');
  assert.equal(root.querySelector('[role="status"]'),status);
  assert.match(status.textContent,/0 matching items/);
  assert(status.isConnected);
  assert(!observer.takeRecords().some(r=>[...r.removedNodes].some(n=>n===status||n.contains?.(status))));
  observer.disconnect();
});

test('closing an item hidden by filters restores a visible logical control',()=>{
  const {dom,root,change}=fixture();
  root.querySelector('[data-pr-item="A"]').click();
  change('[data-pr-state]','done');
  root.querySelector('[data-pr-close]').click();
  assert.equal(dom.window.document.activeElement,root.querySelector('[data-pr-search]'));
  assert.equal(root.querySelector('.pr-detail'),null);
});

test('readable-list items expose the same selected state as work-map items',()=>{
  const {root}=fixture();
  root.querySelector('[data-pr-item="A"]').click();
  root.querySelector('[data-pr-view="list"]').click();
  assert.equal(root.querySelector('.pr-list-item[data-pr-item="A"]').getAttribute('aria-pressed'),'true');
  assert.equal(root.querySelector('.pr-list-item[data-pr-item="B"]').getAttribute('aria-pressed'),'false');
});

test('search retains its input and keyboard focus while updating results',()=>{
  const {dom,root,change}=fixture();
  const search=root.querySelector('[data-pr-search]');
  search.focus();
  change('[data-pr-search]','B','input');
  assert.equal(root.querySelector('[data-pr-search]'),search);
  assert.equal(dom.window.document.activeElement,search);
  assert.equal(root.querySelectorAll('.pr-tile').length,1);
  assert.equal(root.querySelector('.pr-tile').dataset.prItem,'B');
});

test('ordinary inspector close returns focus to the matching work control',()=>{
  const {dom,root}=fixture();
  root.querySelector('[data-pr-item="A"]').click();
  assert.equal(dom.window.document.activeElement,root.querySelector('[data-pr-close]'));
  root.querySelector('[data-pr-close]').click();
  assert.equal(dom.window.document.activeElement,root.querySelector('.pr-tile[data-pr-item="A"]'));
});

test('unbranded component state colours provide readable text contrast',async()=>{
  const {readFile}=await import('node:fs/promises');
  const css=await readFile(new URL('../web/components.css',import.meta.url),'utf8');
  const dom=new JSDOM('<style>'+css+'</style><div data-project-record></div>');
  const style=dom.window.getComputedStyle(dom.window.document.querySelector('[data-project-record]'));
  const luminance=hex=>{
    assert.match(hex,/^#[0-9a-f]{3}(?:[0-9a-f]{3})?$/i,'Default state colours need an explicit contrasting pair');
    const full=hex.length===4?'#'+[...hex.slice(1)].map(c=>c+c).join(''):hex;
    const channels=[1,3,5].map(i=>parseInt(full.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
    return channels.reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  };
  for(const role of ['accent','active','blocked']){
    const back=style.getPropertyValue('--pr-'+role).trim();
    const fore=style.getPropertyValue('--pr-on-'+role).trim();
    const values=[luminance(back),luminance(fore)].sort((a,b)=>a-b);
    assert((values[1]+.05)/(values[0]+.05)>=4.5,role+' default text contrast');
  }
});

test('committing a search edit does not replace its input or lose focus',()=>{
  const {dom,root,change}=fixture();
  const search=root.querySelector('[data-pr-search]');
  search.focus();
  change('[data-pr-search]','B','input');
  search.dispatchEvent(new dom.window.Event('change',{bubbles:true}));
  assert.equal(root.querySelector('[data-pr-search]'),search);
  assert.equal(dom.window.document.activeElement,search);
});
