const deliveryEscape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const deliveryPercent = value => value === null || value === undefined ? 'Not measured' : value.toFixed(1) + '%';
const deliveryPP = value => value === null ? 'Not measured' : (value > 0 ? '+' : '') + value.toFixed(2) + ' pp';

/** Mounts history and delivery views with project-owned typography and colours. */
export function mountDelivery(root, record, options = {}) {
  root.dataset.projectDelivery = '';
  const view = {section:'history', measure:record.project.id==='portfolio'?'ledger':'work', observation:null};
  const history = record.history || {snapshots:[], comparisons:[], coverage:'No history mapped.'};
  const delivery = record.deliverySummary || {plans:[],unreleased:[],releases:[],deployments:[],coverage:'Delivery records have not been mapped.'};
  const h = deliveryEscape;
  const urlLink = (url,label='Observed channel ↗') => {try {const u=new URL(url);return ['http:','https:'].includes(u.protocol)?`<a href="${h(u.href)}" target="_blank" rel="noopener noreferrer">${h(label)}</a>`:'';}catch{return '';}};
  const sourceName = point => (point.source.commit || point.source.sha256).slice(0,8);
  const ids = (title, values) => `<details><summary>${h(title)} · ${values.length}</summary>${values.length?'<ul>'+values.map(id=>`<li>${record.items.some(i=>i.id===id)?'<button type="button" data-delivery-item="'+h(id)+'">'+h(id)+'</button>':h(id)}</li>`).join('')+'</ul>':'<p>None in this comparison.</p>'}</details>`;

  function historyHTML() {
    const points = history.snapshots;
    const measure = view.measure;
    const controls = `<label>History measure<select aria-label="History measure" data-delivery-measure><option value="work"${measure==='work'?' selected':''}>Required scope</option><option value="ledger"${measure==='ledger'?' selected':''}>Retained ledger</option></select></label>`;
    const selected = view.observation === null ? points.length - 1 : view.observation;
    const point = points[selected];
    const measured = points.filter(p=>Number.isFinite(p.metrics[measure].percent));
    const inspection = point ? `<label class="pd-observation-control">Inspect observation<select aria-label="Inspect observation" data-history-observation>${points.map((p,i)=>`<option value="${i}"${i===selected?' selected':''}>${i+1} · ${h(p.observedOn)} · ${deliveryPercent(p.metrics[measure].percent)} · ${p.metrics[measure].done}/${p.metrics[measure].total} · ${h(sourceName(p))}</option>`).join('')}</select></label><p class="pd-observation"><strong>${deliveryPercent(point.metrics[measure].percent)}</strong><span>${point.metrics[measure].done}/${point.metrics[measure].total} ${measure==='work'?'required':'retained'} work items completed<br>Observation ${selected+1} · ${h(point.observedOn)} · source ${h(sourceName(point))}</span></p>` : '';
    const chart = measured.length ? `<figure class="pd-history-figure"><div data-history-plot></div><figcaption>Observations in source order, equally spaced; horizontal distance does not represent elapsed time. Gaps in measured values are left open. All ${points.length} source observations remain in the table.</figcaption></figure>` : '<p>No measured denominator is available.</p>';
    const rows = points.map(p=>`<tr><th scope="row">${h(p.observedOn)}<small>${h(sourceName(p))}</small></th><td>${p.metrics[measure].done}/${p.metrics[measure].total}</td><td>${deliveryPercent(p.metrics[measure].percent)}</td></tr>`).join('');
    const comparisons = history.comparisons.map((c,i)=>{
      const b=c.bridges[measure];
      return `<article class="pd-comparison"><h4>What changed · ${h(points[i].observedOn)} → ${h(points[i+1].observedOn)}</h4><div class="pd-bridge"><div><span>State changes on earlier scope</span><strong>${deliveryPP(b.stateEffectPP)}</strong></div><div><span>Scope and membership changes</span><strong>${deliveryPP(b.scopeEffectPP)}</strong></div><div><span>Total percentage change</span><strong>${deliveryPP(b.totalChangePP)}</strong></div></div><p>${b.before.done}/${b.before.total} → ${b.afterStateChanges.done}/${b.afterStateChanges.total} after state changes → ${b.after.done}/${b.after.total} after scope changes.</p>${ids('Added work',c.added)}${ids('Removed work',c.removed)}${ids('Required-scope changes',c.scopeChanges.map(x=>x.id))}${ids('State changes',c.stateChanges.map(x=>x.id))}${ids('Completion regressions',c.regressions.map(x=>x.id))}<details><summary>Calculation and change-control limits</summary><p>${h(b.method)}</p><p>The comparison observes a change; it does not establish who approved it. Check the linked source history and the governance change record.</p></details></article>`;
    }).join('');
    return `<h3>Progress history</h3><p>${h(history.coverage)}</p>${controls}${inspection}${chart}<table><caption>Exact observation counts</caption><thead><tr><th scope="col">Observation / source</th><th scope="col">Done / scope</th><th scope="col">Progress</th></tr></thead><tbody>${rows}</tbody></table>${points.length<2?'<p>A second pinned snapshot is needed to explain change over time.</p>':''}${comparisons}<p class="pd-note">These percentages measure completed leaves. They do not estimate effort, earned value, schedule efficiency or business benefit.</p>`;
  }

  function drawHistory() {
    const host=root.querySelector('[data-history-plot]');
    if(!host)return;
    const points=history.snapshots;
    const width=Math.max(260,Math.min(900,root.getBoundingClientRect().width || 640));
    const left=42, right=width-66, top=26, bottom=190;
    const x=i=>points.length===1?(left+right)/2:left+i*(right-left)/(points.length-1);
    const y=value=>bottom-value*(bottom-top)/100;
    const selected=view.observation===null?points.length-1:view.observation;
    const tickCount=width<400?2:width<700?3:5;
    const ticks=[...new Set(Array.from({length:Math.min(tickCount,points.length)},(_,i)=>Math.round(i*(points.length-1)/Math.max(1,Math.min(tickCount,points.length)-1))))];
    let path='',open=false,last=-1;
    const marks=points.map((p,i)=>{
      const m=p.metrics[view.measure];
      if(!Number.isFinite(m.percent)){open=false;return '';}
      path+=`${open?'L':'M'}${x(i)},${y(m.percent)} `;open=true;last=i;
      return `<circle cx="${x(i)}" cy="${y(m.percent)}" r="${i===selected?5:3}" class="${i===selected?'pd-selected-point':'pd-point'}"><title>Observation ${i+1} · ${h(p.observedOn)} · ${m.done}/${m.total} · ${deliveryPercent(m.percent)} · source ${h(sourceName(p))}</title></circle>`;
    }).join('');
    const measureLabel=view.measure==='work'?'Required-scope':'Retained-ledger';
    host.innerHTML=`<svg viewBox="0 0 ${width} 246" role="img" aria-label="${measureLabel} progress across ${points.length} source observations, equally spaced rather than elapsed time"><title>${measureLabel} observations; exact values in the observation table</title><desc>Zero to 100 percent. Observations with no measured denominator leave a gap. Select an observation with the Inspect observation control for its date, source, fraction and percentage.</desc>${[0,50,100].map(p=>`<path d="M${left} ${y(p)}H${right}" class="pd-grid"/><text x="${left-8}" y="${y(p)+4}" text-anchor="end">${p}%</text>`).join('')}<path d="${path}" class="pd-line"/>${marks}${last>=0?`<text class="pd-end-label" x="${x(last)+9}" y="${y(points[last].metrics[view.measure].percent)+4}">${deliveryPercent(points[last].metrics[view.measure].percent)}</text>`:''}${ticks.map(i=>`<text x="${x(i)}" y="214" text-anchor="middle">${i+1}</text>`).join('')}<text x="${left}" y="240">Observation</text></svg>`;
  }

  function readinessHTML() {
    return `<h3>Release readiness</h3><p>${h(delivery.coverage)}</p>${delivery.plans.length?delivery.plans.map(plan=>`<article class="pd-release"><span class="pd-kicker">${h(plan.component)} / ${h(plan.channel)}</span><h4>${h(plan.version || plan.id)}</h4><p class="pd-readiness"><strong>${deliveryPercent(plan.percent)}</strong> ${plan.passed}/${plan.total} declared gates met</p><p>${h(plan.status.replaceAll('-',' '))}. Publication remains a separate observation.</p><ul class="pd-gates">${plan.gates.map(g=>`<li><span>${g.status==='passed'?'✓':g.status==='failed'?'!':'○'} ${h(g.label)}</span><strong>${h(g.status)}</strong>${g.basis?'<small>'+h(g.basis)+'</small>':''}${g.receipts?.length?'<details><summary>Inspect '+g.receipts.length+' evidence record(s)</summary><ul>'+g.receipts.map(r=>'<li>'+h(r.kind)+' · '+h(r.result)+' · '+(urlLink(r.source,'Open evidence ↗') || h(r.source))+'<small>Subject '+h(r.subject)+' / '+h(r.revision)+'</small></li>').join('')+'</ul></details>':''}</li>`).join('')}</ul><details><summary>Candidate identity</summary><p>${h(plan.id)} · ${h(plan.revision)}</p></details></article>`).join(''):'<p>No release candidate is mapped. Readiness is not assessed; it is not zero percent.</p>'}`;
  }

  function changesHTML() {
    return `<h3>Changes, publications and deployments</h3><p>${h(delivery.coverage)}</p><h4>Unreleased authored changes</h4><p>These changes have no publication in any mapped channel.</p>${delivery.unreleased.length?'<ul>'+delivery.unreleased.map(c=>'<li><strong>'+h(c.component)+' / '+h(c.type)+'</strong> '+h(c.summary)+'<small>'+h(c.id)+'</small></li>').join('')+'</ul>':'<p>No authored unreleased changes mapped. Coverage may be incomplete.</p>'}<h4>Observed publications</h4>${delivery.releases.length?delivery.releases.map(r=>`<article><strong>${h(r.component)} ${h(r.version)} / ${h(r.channel)}</strong><p>Published ${h(r.publishedAt || 'time unknown')} · observed ${h(r.observedAt)}</p>${urlLink(r.url)}<details><summary>Exact published identity</summary><p>${h(r.revision || r.artifactDigest)}</p></details></article>`).join(''):'<p>No publication observations mapped. A tag or changelog heading alone does not establish distribution.</p>'}<h4>Observed deployments</h4>${delivery.deployments.length?delivery.deployments.map(d=>`<article><strong>${h(d.environment)} · ${h(d.health || 'unknown')}</strong><p>Deployed ${h(d.deployedAt || 'time unknown')} · observed ${h(d.observedAt)}</p><p>${urlLink(d.url,'Open deployment ↗')} ${urlLink(d.source,'Deployment evidence ↗')}</p><details><summary>Deployed identity</summary><p>${h(d.revision || d.artifactDigest)}</p></details></article>`).join(''):'<p>No environment observations mapped. A merged change does not establish deployment.</p>'}`;
  }

  function render() {
    root.innerHTML = `<div class="pd-navigation" role="group" aria-label="Tracking sections">${[['history','Progress history'],['readiness','Release readiness'],['changes','Changelog & deployments']].map(([value,label])=>`<button type="button" data-delivery-section="${value}" aria-pressed="${view.section===value}">${label}</button>`).join('')}</div><section class="pd-content">${view.section==='history'?historyHTML():view.section==='readiness'?readinessHTML():changesHTML()}</section>`;
    drawHistory();
  }
  const resizeObserver = typeof root.ownerDocument.defaultView.ResizeObserver === 'function' ? new root.ownerDocument.defaultView.ResizeObserver(()=>drawHistory()) : null;
  resizeObserver?.observe(root);
  const onClick = event => {
    const button=event.target.closest('button');
    if(!button || !root.contains(button))return;
    if(button.dataset.deliverySection){view.section=button.dataset.deliverySection;render();root.querySelector(`[data-delivery-section="${view.section}"]`)?.focus();}
    if(button.dataset.deliveryItem)options.onItem?.(button.dataset.deliveryItem);
  };
  const onChange = event => {
    if(event.target.matches('[data-delivery-measure]')){view.measure=event.target.value;render();root.querySelector('[data-delivery-measure]')?.focus();}
    if(event.target.matches('[data-history-observation]')){view.observation=Number(event.target.value);render();root.querySelector('[data-history-observation]')?.focus();}
  };
  root.addEventListener('click',onClick);root.addEventListener('change',onChange);render();
  return {destroy(){resizeObserver?.disconnect();root.removeEventListener('click',onClick);root.removeEventListener('change',onChange);}};
}
