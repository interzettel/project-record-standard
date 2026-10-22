/** Computes labelled leaf progress without adding partial workflow credit. */
export function progress(items, mode = 'required') {
  if (!['required', 'ledger'].includes(mode)) throw new Error('Unknown denominator');
  if (new Set(items.map(i => i.id)).size !== items.length) throw new Error('Duplicate leaf ID');
  const selected = items.filter(i => i.state !== 'cancelled' && (mode === 'ledger' || i.required));
  const done = selected.filter(i => i.state === 'done').length;
  return {done, total:selected.length, percent:selected.length ? Math.round(1000 * done / selected.length) / 10 : null,
    active:selected.filter(i => i.state === 'active').length, review:selected.filter(i => i.state === 'review').length,
    blocked:selected.filter(i => i.blocked).length, excluded:items.length - selected.length};
}

/** Selects work by stable identity, workflow state and retained scope. */
export function selectItems(record, {milestone='', state='all', query='', mode='required'} = {}) {
  const term = query.trim().toLowerCase();
  return record.items.filter(i => (!milestone || i.milestoneId === milestone)
    && (mode === 'ledger' || i.required)
    && (state === 'all' || (state === 'blocked' ? i.blocked : state === 'deferred' ? !i.required : i.state === state))
    && (!term || [i.id,i.title,i.owner,i.kind,i.priority,i.note].filter(Boolean).join(' ').toLowerCase().includes(term)));
}

/** Keeps absent, failed, superseded and wrong-revision receipts from passing. */
export function policySatisfied(policy, receipts, subject, revision = null) {
  const all = policy.allOf || [], any = policy.anyOf || [];
  if (!all.length && !any.length) return false;
  const kinds = new Set(receipts.filter(r => r.result === 'passed' && r.subject === subject
    && !r.supersededBy && (revision === null || r.revision === revision)).map(r => r.kind));
  return all.every(k => kinds.has(k)) && (!any.length || any.some(k => kinds.has(k)));
}
