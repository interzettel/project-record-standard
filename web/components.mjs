import {progress, selectItems} from './metrics.mjs';

const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pct = value => value === null ? 'Not measured' : value.toFixed(1) + '%';
const stateName = item => item.blocked ? 'Blocked' : ({done:'Done',active:'In progress',review:'In review',ready:'Ready',backlog:'Planned',cancelled:'Cancelled',unknown:'Unknown'}[item.state]);
const stateMark = item => item.blocked ? '!' : ({done:'✓',active:'→',review:'↗',ready:'○',backlog:'·',cancelled:'×',unknown:'?'}[item.state]);
const safeURL = value => {try {const u = new URL(value);return ['https:','http:'].includes(u.protocol) ? u.href : null;} catch {return null;}};

/** Renders a meter and its exact numerator without choosing host typography. */
export function meterHTML(metric, label) {
  return `<div class="pr-meter-label"><span>${escapeHTML(label)}</span><strong>${pct(metric.percent)}</strong></div>
    <div class="pr-meter" role="progressbar" aria-label="${escapeHTML(label)}" aria-valuemin="0" aria-valuemax="${metric.total || 1}" ${metric.total?'aria-valuenow="'+metric.done+'"':''} aria-valuetext="${metric.total ? metric.done+' of '+metric.total : 'Not measured; no denominator'}"><span style="width:${metric.percent || 0}%"></span></div>
    <span class="pr-count">${metric.done} / ${metric.total} · ${escapeHTML(metric.method || 'completed / selected items')}</span>`;
}

/** Mounts the optional work explorer inside an existing project-owned shell.
 * @param {HTMLElement} root The host element, whose font and tokens are inherited.
 * @param {object} record The validated normalized snapshot.
 * @param {object} options The initial milestone and optional host event callback.
 * @returns {{selectMilestone: Function, selectItem: Function, destroy: Function}} The local view controls.
 */
export function mountExplorer(root, record, options = {}) {
  const state = {milestone:options.milestone || '', state:'all', query:'', mode:'required', view:'map', selected:options.item || null};
  root.dataset.projectRecord = '';
  const milestones = new Map(record.milestones.map(m => [m.id,m]));
  const groups = new Map(record.groups.map(g => [g.id,g]));
  const items = new Map(record.items.map(i => [i.id,i]));
  const label = name => escapeHTML(name);
  const navOption = (value,text,current) => `<option value="${label(value)}"${value===current?' selected':''}>${label(text)}</option>`;
  root.innerHTML = '<div data-pr-controls></div><div class="pr-selection-summary"><div data-pr-meter></div><p role="status" aria-live="polite" aria-atomic="true"></p></div><div data-pr-results></div>';

  function detail(item) {
    const linked = id => `<button type="button" class="pr-inline" data-pr-item="${label(id)}">${label(id)}</button>`;
    const evidence = item.evidence.map(e => {
      const url = safeURL(e.source);
      return `<li>${label(e.kind)} · ${url?`<a href="${label(url)}" target="_blank" rel="noopener noreferrer">Source receipt ↗</a>`:label(e.source)}</li>`;
    }).join('');
    return `<section class="pr-detail" aria-label="Selected work item"><div class="pr-detail-head"><div><span class="pr-id">${label(item.id)}</span><h3>${label(item.title)}</h3></div><button type="button" data-pr-close>Close</button></div>
      <p class="pr-state ${item.blocked?'is-blocked':item.state==='done'?'is-done':''}">${label(stateName(item))} · source state: ${label(item.sourceState)}</p>
      <dl><dt>Purpose and acceptance</dt><dd>${label(item.criterion || 'The source ledger names this work; detailed acceptance is not mapped into this record yet.')}</dd>
      <dt>Owner / priority</dt><dd>${label(item.owner || 'Unassigned')} · ${label(item.priority || 'Not set')}</dd>
      <dt>Scope</dt><dd>${label(item.milestoneId || 'No milestone mapped')} / ${label(item.groupId)} · ${item.required?'required in this scope':'deferred from this scope'}</dd>
      <dt>Dependencies</dt><dd>${item.dependsOn.length?item.dependsOn.map(linked).join(' · '):label(item.dependencyCoverage==='not-declared'?'Not declared in source':'No declared prerequisite')}${item.unmappedDependencies.length?'<p>Unmapped: '+label(item.unmappedDependencies.join(', '))+'</p>':''}</dd>
      <dt>Evidence</dt><dd>${evidence?'<ul>'+evidence+'</ul>':'No typed receipt mapped. The source claim is retained without inventing evidence.'}</dd></dl>
      ${item.note?'<p class="pr-note">'+label(item.note)+'</p>':''}${item.deferReason?'<p class="pr-note">Deferral: '+label(item.deferReason)+'</p>':''}
      ${safeURL(item.issueUrl)?'<a href="'+label(safeURL(item.issueUrl))+'" target="_blank" rel="noopener noreferrer">Open owning GitHub issue ↗</a>':''}</section>`;
  }

  function results() {
    const selected = selectItems(record,state);
    const scopeItems = record.items.filter(i => !state.milestone || i.milestoneId === state.milestone);
    const metric = progress(scopeItems,state.mode);
    const milestone = milestones.get(state.milestone);
    root.querySelector('[data-pr-meter]').innerHTML = meterHTML({...metric,method:state.mode==='ledger'?'completed / retained ledger items':'completed / required scope items'},milestone?milestone.id+' · '+milestone.title:'Selected denominator');
    const status = root.querySelector('[role="status"]');
    const announcement = `${selected.length} matching items · ${metric.blocked} blocked in scope · ${metric.excluded} outside this denominator`;
    if(status.textContent!==announcement)status.textContent=announcement;
    const block = state.view==='list' ? `<div class="pr-list">${selected.map(i=>`<button type="button" class="pr-list-item" data-pr-item="${label(i.id)}" aria-pressed="${state.selected===i.id}"><span class="pr-id">${label(i.id)}</span><span>${label(i.title)}</span><span class="pr-state ${i.blocked?'is-blocked':i.state==='done'?'is-done':''}">${label(stateName(i))}</span></button>`).join('')}</div>` : [...groups.values()].filter(g=>selected.some(i=>i.groupId===g.id)).map(g=>{
      const own = selected.filter(i=>i.groupId===g.id);
      const all = scopeItems.filter(i=>i.groupId===g.id);
      const metric = progress(all,state.mode);
      return `<section class="pr-work-group"><div class="pr-group-head"><h3>${label(g.id)} · ${label(g.title)}</h3><span>${pct(metric.percent)} · ${metric.done}/${metric.total}</span></div>
        <div class="pr-tiles">${own.map(i=>`<button type="button" class="pr-tile ${i.blocked?'is-blocked':i.state==='done'?'is-done':i.state==='active'?'is-active':''}" data-pr-item="${label(i.id)}" aria-label="${label(i.id+' · '+i.title+' · '+stateName(i))}" aria-pressed="${state.selected===i.id}"><span aria-hidden="true">${stateMark(i)} </span>${label(i.id)}</button>`).join('')}</div></section>`;
    }).join('');
    return (state.selected && items.has(state.selected)?detail(items.get(state.selected)):'') + (selected.length?block:'<p class="pr-empty">No work matches these filters.</p>');
  }

  function render() {
    root.querySelector('[data-pr-controls]').innerHTML = `<div class="pr-controls"><label>Milestone<select data-pr-milestone aria-label="Milestone">${navOption('','All milestones',state.milestone)}${record.milestones.map(m=>navOption(m.id,m.id+' · '+m.title,state.milestone)).join('')}</select></label>
      <label>Status<select data-pr-state aria-label="Status">${[['all','All states'],['done','Done'],['active','In progress'],['review','In review'],['ready','Ready'],['blocked','Blocked'],['backlog','Planned'],['deferred','Deferred'],['cancelled','Cancelled'],['unknown','Unknown']].map(([v,t])=>navOption(v,t,state.state)).join('')}</select></label>
      <label>Denominator<select data-pr-mode aria-label="Denominator">${navOption('required','Required scope',state.mode)}${navOption('ledger','Retained ledger',state.mode)}</select></label>
      <label class="pr-search">Find work<input type="search" data-pr-search value="${label(state.query)}" placeholder="ID, title, owner, kind…"></label></div>
      <div class="pr-view-row"><div><button type="button" data-pr-view="map" aria-pressed="${state.view==='map'}">Work map</button><button type="button" data-pr-view="list" aria-pressed="${state.view==='list'}">Readable list</button></div><span class="pr-legend"><span class="is-done">✓ Done</span><span class="is-active">→ In progress</span><span class="is-blocked">! Blocked</span><span>· Planned</span></span></div>`;
    root.querySelector('[data-pr-results]').innerHTML=results();
  }

  const onClick = event => {
    const button = event.target.closest('button');
    if (!button || !root.contains(button)) return;
    const priorItem = state.selected;
    if ('prItem' in button.dataset) {
      state.selected=button.dataset.prItem;
      const target=items.get(state.selected);
      if(target && state.milestone && target.milestoneId!==state.milestone){state.milestone=target.milestoneId || '';state.state='all';state.query='';}
      if(target && !target.required)state.mode='ledger';
    }
    if ('prView' in button.dataset) state.view=button.dataset.prView;
    if ('prClose' in button.dataset) state.selected=null;
    render();
    if ('prItem' in button.dataset) {root.querySelector('[data-pr-close]')?.focus();root.querySelector('.pr-detail')?.scrollIntoView({block:'nearest'});}
    if ('prClose' in button.dataset) {
      const origin = [...root.querySelectorAll('[data-pr-item]')].find(b=>b.dataset.prItem===priorItem);
      (origin || root.querySelector('[data-pr-search]'))?.focus();
    }
    if ('prView' in button.dataset) root.querySelectorAll('[data-pr-view]').forEach(b=>{if(b.dataset.prView===state.view)b.focus();});
    options.onSelection?.({milestone:state.milestone,item:state.selected});
  };
  const onChange = event => {
    const focusSelector = ['[data-pr-milestone]','[data-pr-state]','[data-pr-mode]'].find(selector=>event.target.matches(selector));
    if(!focusSelector)return;
    if (event.target.matches('[data-pr-milestone]')) {state.milestone=event.target.value;state.selected=null;}
    if (event.target.matches('[data-pr-state]')) {state.state=event.target.value;if(state.state==='deferred')state.mode='ledger';}
    if (event.target.matches('[data-pr-mode]')) state.mode=event.target.value;
    render();
    if(focusSelector)root.querySelector(focusSelector)?.focus();
    options.onSelection?.({milestone:state.milestone,item:state.selected});
  };
  const onInput = event => {
    if (!event.target.matches('[data-pr-search]')) return;
    state.query=event.target.value;
    root.querySelector('[data-pr-results]').innerHTML=results();
  };
  root.addEventListener('click',onClick);root.addEventListener('change',onChange);root.addEventListener('input',onInput);
  render();
  return {selectMilestone(id){if(id && !milestones.has(id))throw new Error('Unknown milestone');state.milestone=id;state.selected=null;render();},selectItem(id){if(!items.has(id))throw new Error('Unknown work item');state.selected=id;if(!items.get(id).required)state.mode='ledger';render();},destroy(){root.removeEventListener('click',onClick);root.removeEventListener('change',onChange);root.removeEventListener('input',onInput);}};
}
