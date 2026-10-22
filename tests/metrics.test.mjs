import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {progress,selectItems,policySatisfied} from '../web/metrics.mjs';

for (const project of ['prehnite','standard']) {
  const record=JSON.parse(fs.readFileSync(new URL('../.record-build/'+project+'/record.json',import.meta.url)));
  test(project+' browser percentages agree with offline calculation',()=>{
    for (const [mode,key] of [['required','work'],['ledger','ledger']]) {
      const value=progress(record.items,mode);
      for (const field of ['done','total','percent','blocked','excluded']) assert.equal(value[field],record.metrics[key][field]);
    }
  });
  test(project+' search, scope and workflow filters select the real records',()=>{
    const sample=record.items[0];
    assert(selectItems(record,{query:sample.id,mode:'ledger'}).some(i=>i.id===sample.id));
    assert(selectItems(record,{milestone:sample.milestoneId,mode:'ledger'}).every(i=>i.milestoneId===sample.milestoneId));
    assert(selectItems(record,{state:'blocked',mode:'ledger'}).every(i=>i.blocked));
    assert.equal(selectItems(record,{query:'no-matching-identifier-999'}).length,0);
  });
}
test('deferred work needs an explicit ledger denominator',()=>{
  const record={items:[{id:'LATER',title:'Deferred fixture',state:'backlog',required:false,blocked:false}]};
  assert.equal(selectItems(record,{mode:'ledger'}).length,1);
  assert.equal(selectItems(record,{mode:'required'}).length,0);
});
test('all-required evidence cannot be satisfied by one matching kind',()=>{
  const policy={allOf:['experiment','review'],anyOf:[]};
  const receipt={kind:'experiment',result:'passed',subject:'WP1',revision:'r1'};
  assert.equal(policySatisfied(policy,[receipt],'WP1','r1'),false);
  assert.equal(policySatisfied(policy,[receipt,{...receipt,kind:'review'}],'WP1','r1'),true);
  assert.equal(policySatisfied(policy,[receipt,{...receipt,kind:'review',result:'failed'}],'WP1','r1'),false);
});
test('half-tenth leaf percentage uses the shared upward tie rule',()=>{
  const items=Array.from({length:16},(_,i)=>({id:String(i),state:i<13?'done':'backlog',required:true,blocked:false}));
  assert.equal(progress(items).percent,81.3);
});
