"""Builds standalone reference views and embeddable progress records."""

from html import escape
import json
from pathlib import Path
import hashlib

from .core import RecordError, export_record
from .delivery import changelog_markdown, delivery_summary


def _percent(value: float | None) -> str:
    return f"{value:.1f}%" if value is not None else "Not measured"


def _source_url(record: dict) -> str | None:
    if not record['project'].get('repository') or not record['source'].get('commit'):
        return None
    return f"https://github.com/{record['project']['repository']}/blob/{record['source']['commit']}/{record['source']['path']}"


def _source_label(record: dict) -> str:
    return (record['source'].get('commit') or record['source']['sha256'])[:8]


def _standard(record: dict) -> str:
    metrics = record['metrics']
    cards = ''.join(f'<button type="button" class="milestone-card" data-milestone="{escape(m["id"])}"><span class="eyebrow">{escape(m["id"])} / {escape(m["horizon"])}</span><h3>{escape(m["title"])}</h3>{_meter(m["progress"], "Required work")}<span class="outcome-state">{"Milestone accepted" if m["accepted"] else "Acceptance pending"}</span></button>' for m in record['milestones'])
    return f'''<header class="project-header"><span class="project-name">Project record / standard</span><span>Implementation and delivery</span><button type="button" data-appearance>Appearance</button></header><section class="project-intro"><span class="eyebrow">Canonical standard · evidence and acceptance in view</span><h1>Work with a clear record.</h1><p>The standard tracks its own implementation. Source observations, release-candidate checks and owner acceptance have distinct meanings.</p></section><div class="headline-metrics"><div><span>Required work completed</span><strong>{_percent(metrics['work']['percent'])}</strong><small>{metrics['work']['done']}/{metrics['work']['total']} required work items</small></div><div><span>Milestones accepted</span><strong>{_percent(metrics['milestones']['percent'])}</strong><small>{metrics['milestones']['done']}/{metrics['milestones']['total']}</small></div><p>Owner acceptance follows recorded authority decisions; engineering checks alone never grant it.</p></div><section class="phase"><div class="section-head"><h2>Roadmap</h2><span>Open a checkpoint to inspect its work and acceptance criteria</span></div><div class="milestone-grid">{cards}</div></section>'''


def _meter(metric: dict, label: str) -> str:
    return f'<div class="metric-heading"><span>{escape(label)}</span><strong>{_percent(metric["percent"])}</strong></div><div class="meter" role="progressbar" aria-label="{escape(label)}" aria-valuemin="0" aria-valuemax="{metric["total"] or 1}" aria-valuenow="{metric["done"]}" aria-valuetext="{metric["done"]} of {metric["total"]}"><span style="width:{metric["percent"] or 0}%"></span></div><span class="count">{metric["done"]} / {metric["total"]}</span>'


def _prehnite(record: dict) -> str:
    metrics = record["metrics"]
    cards = []
    for phase in dict.fromkeys(g["panel"] for g in record["groups"]):
        own = [m for m in record["milestones"] if any(g["id"] in m["groupIds"] and g["panel"] == phase for g in record["groups"])]
        cards.append(f'<section class="phase"><div class="section-head"><span class="eyebrow">{escape(phase)}</span><h2>{"An efficient workbench on the existing laptop" if phase == "P1" else "Controlled style and appearance experiments"}</h2></div><div class="milestone-grid">')
        for m in own:
            status = "Outcome accepted" if m["accepted"] else "Outcome pending"
            cards.append(f'<button type="button" class="milestone-card {"accepted" if m["accepted"] else ""}" data-milestone="{escape(m["id"])}"><span class="eyebrow">{escape(m["id"])}</span><h3>{escape(m["title"])}</h3>{_meter(m["progress"], "Work verified")}<span class="outcome-state">{status}</span></button>')
        cards.append('</div></section>')
    return f'''<header class="project-header"><a class="project-name" href="https://github.com/interzettel/prehnite">Prehnite</a><span>Make the images. Keep the experiments.</span><button type="button" data-appearance>Appearance</button></header>
    <section class="project-intro"><span class="eyebrow">Development record · source-backed reference</span><h1>Product development</h1><p>Verified supporting work, remaining experiments and accepted outcomes, grouped by phase.</p></section>
    <div class="headline-metrics"><div><span>Engineering evidence</span><strong>{_percent(metrics['work']['percent'])}</strong><small>{metrics['work']['done']} / {metrics['work']['total']} required tasks verified</small></div><div><span>Accepted outcomes</span><strong>{_percent(metrics['milestones']['percent'])}</strong><small>{metrics['milestones']['done']} / {metrics['milestones']['total']} milestones accepted</small></div><p>Verification counts the supporting work. Acceptance follows the milestone's declared outcome gates.</p></div>
    {''.join(cards)}'''


def _portfolio(record: dict) -> str:
    metrics = record["metrics"]
    rows = []
    for m in record["milestones"]:
        g = m["gateProgress"]
        rows.append(f'<button type="button" class="roadmap-row" data-milestone="{escape(m["id"])}"><span class="row-identity"><span class="eyebrow">{escape(m["id"])} / {escape(m["horizon"])}</span><h3>{escape(m["title"])}</h3><span class="row-note">{g["done"]}/{g["total"]} exit criteria met · {"Milestone reached" if m["accepted"] else "Acceptance pending"}</span></span><span class="row-progress">{_meter(m["progress"], "Required work")}</span><span class="row-arrow" aria-hidden="true">↗</span></button>')
    return f'''<header class="project-header"><a class="project-name" href="https://yigitdenktas.com">yigitdenktas.com</a><span>Work / development</span><button type="button" data-appearance>Appearance</button></header>
    <section class="project-intro"><span class="eyebrow">Portfolio, studies and the shared interactive core</span><h1>The work,<br><span>in view.</span></h1><p>{metrics['milestones']['total']} milestones, the work behind them, and the decisions that let each one move forward.</p></section>
    <section class="portfolio-summary"><div class="large-percent"><strong>{_percent(metrics['roadmapMean']['percent'])}</strong><span>Roadmap progress</span><small>Mean of {metrics['milestones']['total']} milestone work percentages.<br>Each milestone has the same weight.</small></div><div class="summary-stack"><div><strong>{metrics['milestones']['done']} / {metrics['milestones']['total']}</strong><span>Milestones reached · {_percent(metrics['milestones']['percent'])}</span></div><div><strong>{_percent(metrics['ledger']['percent'])}</strong><span>Whole ledger · {metrics['ledger']['done']}/{metrics['ledger']['total']} items</span></div><div><strong>{_percent(metrics['work']['percent'])}</strong><span>Required scope · {metrics['work']['done']}/{metrics['work']['total']} items · {metrics['work']['excluded']} deferred</span></div></div></section>
    <section class="portfolio-roadmap"><div class="section-head"><h2>Roadmap</h2><span>Milestone → epic → work item</span></div>{''.join(rows)}</section>'''


def _theme_css(theme: dict) -> str:
    light = ";".join(f"--{k}:{v}" for k, v in theme["light"].items())
    dark = ";".join(f"--{k}:{v}" for k, v in theme["dark"].items())
    return f':root{{{light}}}:root[data-appearance="dark"]{{{dark}}}@media(prefers-color-scheme:dark){{:root:not([data-appearance="light"]){{{dark}}}}}'


BASE_CSS = """
.skip-link{position:absolute;top:-100px;left:18px;background:var(--background);color:var(--text);padding:12px;z-index:10}.skip-link:focus{top:12px}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}body{margin:0;background:var(--background);color:var(--text);font:16px/1.55 var(--host-font);-webkit-font-smoothing:antialiased}button,input,select{font:inherit;color:inherit}button{cursor:pointer}a{color:inherit;text-underline-offset:4px}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid var(--text);outline-offset:4px}.wrap{overflow-wrap:anywhere;max-width:1160px;padding:0 34px 50px;margin:auto}.review-strip{padding:9px 20px;text-align:center;font-size:12px;background:var(--text);color:var(--background)}.project-header{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:24px 0;border-bottom:1px solid var(--border)}.project-header span{font-size:13px;color:var(--muted)}.project-name{min-width:0;overflow-wrap:anywhere;font-weight:700;letter-spacing:-.04em;text-decoration:none;font-size:23px}.project-header button{background:transparent;border:1px solid var(--border);padding:8px 12px;border-radius:5px;font-size:12px}.project-intro{padding:60px 0 42px}.eyebrow{font:12px/1.5 ui-monospace,Consolas,monospace;letter-spacing:.02em;color:var(--signalText)}h1{font-size:clamp(42px,6.7vw,76px);line-height:1.02;letter-spacing:-.05em;margin:19px 0 20px;max-width:15ch}h2{font-size:24px;line-height:1.2;letter-spacing:-.025em;margin:0}h3{line-height:1.35;margin:8px 0 16px;font-size:17px;letter-spacing:-.02em}p{margin:10px 0}.project-intro p{font-size:19px;max-width:48ch;color:var(--muted)}.section-head{display:flex;align-items:baseline;gap:20px;justify-content:space-between;margin-bottom:22px}.section-head>span{font-size:12px;color:var(--muted)}.metric-heading{display:flex;justify-content:space-between;gap:12px;align-items:baseline;font-size:12px}.metric-heading strong{font-size:20px;letter-spacing:-.03em;font-variant-numeric:tabular-nums}.meter{height:7px;background:color-mix(in srgb,var(--text) 13%,var(--background));border-radius:5px;overflow:hidden;margin:8px 0}.meter>span{display:block;height:100%;background:var(--accent)}.count{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}.outcome-state{display:block;font-size:12px;color:var(--muted);margin-top:13px}.headline-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:28px;border-block:1px solid var(--border);padding:26px 0}.headline-metrics>div{min-width:0;display:grid;gap:7px}.headline-metrics strong{font-size:52px;line-height:1.1;letter-spacing:-.05em}.headline-metrics span,.headline-metrics small{font-size:13px}.headline-metrics>div:nth-child(2) strong{color:var(--signalText)}.headline-metrics p{font-size:14px;color:var(--muted);align-self:center}.phase{padding:36px 0 5px}.milestone-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.milestone-card{background:var(--surface);border:1px solid var(--border);padding:19px;border-radius:8px;text-align:left;min-width:0;transition:transform .15s,border-color .15s}.milestone-card:hover{transform:translateY(-3px);border-color:var(--text)}.milestone-card:active{transform:translateY(0)}.milestone-card.accepted{background:color-mix(in srgb,var(--accent) 8%,var(--surface));border-color:var(--accent)}.milestone-card h3{min-height:48px}.explorer-section{padding-top:50px}.explorer-section>p{font-size:14px;color:var(--muted);max-width:70ch;margin-bottom:25px}.source-detail{border-top:1px solid var(--border);margin-top:35px;padding-top:20px;color:var(--muted);font-size:12px;overflow-wrap:anywhere}.source-detail p{max-width:90ch}.source-detail summary{cursor:pointer;min-height:44px;padding:8px 0}.source-detail code{font-family:ui-monospace,Consolas,monospace}.back-to-top{font-size:12px;margin-top:25px}.portfolio-summary{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:40px;padding:36px 0 50px;border-block:1px solid var(--border)}.large-percent{min-width:0;display:grid;gap:7px;align-content:start}.large-percent>strong{overflow-wrap:anywhere;max-width:100%;font-size:clamp(70px,10vw,116px);line-height:1;letter-spacing:-.065em;font-weight:650;font-variant-numeric:tabular-nums}.large-percent>span{font-size:20px;margin-top:12px}.large-percent>small{font-size:13px;color:var(--muted);max-width:34ch}.summary-stack{min-width:0;display:grid;gap:20px}.summary-stack>div{min-width:0;display:grid;gap:3px;padding-bottom:14px;border-bottom:1px solid var(--border)}.summary-stack strong{font-size:28px;letter-spacing:-.04em}.summary-stack span{font-size:12px;color:var(--muted)}.portfolio-roadmap{margin-top:46px}.roadmap-row{width:100%;text-align:left;display:grid;grid-template-columns:1.4fr 1fr 25px;align-items:center;gap:30px;background:var(--surface);border:1px solid var(--border);border-radius:18px;margin:12px 0;padding:21px 25px;transition:transform .17s,background .17s}.roadmap-row:hover{transform:translateX(3px);background:color-mix(in srgb,var(--signal) 7%,var(--surface))}.roadmap-row h3{margin:5px 0 7px}.row-note{font-size:12px;color:var(--muted)}.row-progress .metric-heading>span{font-size:11px}.row-progress .metric-heading>strong{font-size:27px}.row-arrow{font-size:24px;align-self:center}.portfolio .project-intro h1>span{color:var(--muted)}.portfolio .eyebrow{color:var(--muted)}.portfolio .project-header button{border-radius:999px}.portfolio .section-head h2{font-size:34px}.portfolio [data-project-record]{--pr-radius:10px}.prehnite .section-head .eyebrow{color:var(--signalText)}.prehnite .project-name{text-transform:uppercase;letter-spacing:-.035em}.pr-host{--pr-accent:var(--accent);--pr-on-accent:var(--accentText);--pr-surface:var(--surface);--pr-muted:var(--muted);--pr-line:var(--border);--pr-track:color-mix(in srgb,var(--text) 12%,var(--background));--pr-active:#797d86;--pr-blocked:var(--signalText);--pr-option-text:var(--text);--pr-option-surface:var(--surface)}.criterion-box{padding:20px;border:1px solid var(--border);margin:0 0 24px;border-radius:8px}.criterion-box>h3{margin:6px 0 10px}.criterion-box [data-milestone-title]:focus{outline:3px solid var(--text);outline-offset:4px}.criterion-box p,.criterion-box li{font-size:14px;color:var(--muted)}.criterion-box ul{padding-left:18px}.criterion-box .gates{display:flex;gap:15px;flex-wrap:wrap;font-size:12px;margin-top:15px}.criterion-box a{color:inherit}.plain-button{background:var(--accent);color:var(--accentText);border:0;border-radius:8px;padding:11px 16px;font-size:13px;margin-top:14px}.portfolio .plain-button{background:var(--signal);color:var(--signalText);border-radius:12px}.evidence-notice{margin:18px 0;font-size:12px;color:var(--muted)}
@media(max-width:800px){.milestone-grid{grid-template-columns:1fr 1fr}.headline-metrics{grid-template-columns:1fr 1fr}.headline-metrics>p{grid-column:1/-1;margin:0}.roadmap-row{grid-template-columns:1.3fr 1fr;gap:20px}.row-arrow{display:none}.wrap{padding-inline:24px}.project-header>span{display:none}}
@media(max-width:500px){.wrap{padding-inline:18px}.project-intro{padding:35px 0 28px}.project-intro p{font-size:17px}.milestone-grid,.portfolio-summary{grid-template-columns:1fr}.headline-metrics{gap:16px}.headline-metrics strong{font-size:39px}.milestone-card h3{min-height:0}.section-head{display:block}.section-head>span{display:block;margin-top:10px}.section-head h2{margin-top:8px}.roadmap-row{grid-template-columns:1fr;padding:19px;gap:13px}.portfolio-summary{gap:28px}.summary-stack{grid-template-columns:1fr 1fr}.summary-stack>div:last-child{grid-column:1/-1}.milestone-card{padding:16px}.project-header{padding:20px 0;gap:10px}.project-name{font-size:19px}.project-header button{font-size:11px}.criterion-box{padding:16px}}
.prehnite .project-intro{padding:28px 0 25px}.prehnite .project-intro h1{font-size:34px;letter-spacing:-.025em;line-height:1.12;max-width:none;text-transform:uppercase;margin:13px 0}.prehnite .project-intro p{font-size:15px;max-width:75ch}.prehnite .headline-metrics strong{font-size:43px}.prehnite .phase{padding-top:28px}.prehnite .section-head{justify-content:start}.prehnite .section-head h2{font-size:19px}
.pr-host{--pr-focus:var(--text);--pr-active:#686d77;--pr-on-active:#fff;--pr-blocked:var(--blocked,var(--signalText));--pr-on-blocked:var(--background);--pr-selection:var(--text)}[data-project-record] .pr-tile[aria-pressed=true]{outline-color:var(--pr-selection,currentColor)}
@media(max-width:500px){.prehnite .project-intro h1{font-size:28px}.prehnite .headline-metrics strong{font-size:36px}}
@media(max-width:400px){.project-header{flex-wrap:wrap}.headline-metrics,.summary-stack{grid-template-columns:minmax(0,1fr)}.summary-stack>div:last-child{grid-column:auto}.headline-metrics>p{grid-column:auto}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important;transform:none!important}}
"""


def render_html(record: dict, theme: dict, toolkit_root: Path) -> str:
    """Builds a self-contained project-owned reference presentation.

    Args:
        record: The summarized normalized source record.
        theme: The project's sourced presentation tokens and typography.
        toolkit_root: The standard checkout containing the browser components.

    Returns:
        The standalone HTML with inline data, styles and local interactions.
    """
    project = record["project"]["id"]
    if project not in {"prehnite", "portfolio", "standard"}:
        raise RecordError("No reference presentation registered; export the record into the project's own site renderer")
    css = (toolkit_root / "web/components.css").read_text() + (toolkit_root / "web/delivery.css").read_text()
    metrics_js = (toolkit_root / "web/metrics.mjs").read_text().replace("export function", "function")
    component_js = (toolkit_root / "web/components.mjs").read_text().replace("import {progress, selectItems} from './metrics.mjs';", "").replace("export function", "function")
    component_js += "\n" + (toolkit_root / "web/delivery.mjs").read_text().replace("export function", "function")
    body = _prehnite(record) if project == "prehnite" else _portfolio(record) if project == "portfolio" else _standard(record)
    model = json.dumps(record, ensure_ascii=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    mode_note = ("Content-addressed ledger snapshot; hosted evidence is recorded separately" if record["source"].get("kind") == "file-snapshot" else "Public repository snapshot") if record["project"]["visibility"] == "public" else "Owner review copy · private source fixture · not a publication approval"
    script = metrics_js + "\n" + component_js + "\n" + r'''
const record = JSON.parse(document.getElementById('record-data').textContent);
function writeSelection(selection) {
  const parameters = new URLSearchParams();
  if(selection.milestone) parameters.set('m',selection.milestone);
  if(selection.item) parameters.set('item',selection.item);
  const hash=parameters.toString();
  if(location.hash.slice(1)!==hash) history.pushState(selection,'',hash?'#'+hash:location.pathname);
}
const explorer = mountExplorer(document.getElementById('work-explorer'),record,{onSelection:selection=>{renderMilestoneDetail(selection.milestone);writeSelection(selection);}});
const detail = document.getElementById('milestone-detail');
mountDelivery(document.getElementById('delivery-explorer'),record,{onItem:id=>{const item=record.items.find(i=>i.id===id);if(item?.milestoneId)showMilestone(item.milestoneId);explorer.selectItem(id);writeSelection({milestone:item?.milestoneId,item:id});document.querySelector('[data-pr-close]')?.focus();}});
const e = escapeHTML;
function renderMilestoneDetail(id) {
  const m = record.milestones.find(m=>m.id===id);
  if(!m){detail.innerHTML='';return false;}
  const index = new Map(record.items.map(i=>[i.id,i]));
  const gates = m.gateItemIds.map(id=>index.get(id));
  const openGates = gates.filter(i=>i.state!=='done');
  const metGates = gates.filter(i=>i.state==='done');
  detail.innerHTML = `<div class="criterion-box"><span class="eyebrow">${e(m.id)} · ${e(m.horizon)}</span><h3 data-milestone-title tabindex="-1">${e(m.title)}</h3><p>${e(m.goal)}</p>
    <div class="gates"><span>${m.progress.done}/${m.progress.total} required items · ${m.progress.percent===null?'Not measured':m.progress.percent.toFixed(1)+'%'}</span><span>${m.accepted?'Milestone accepted':'Milestone acceptance pending'}</span></div>
    ${m.nextAction?'<p><strong>Next action:</strong> '+e(m.nextAction)+'</p>':''}
    <h3 style="margin-top:20px">${openGates.length?'Remaining exit criteria':'Declared exit criteria met'}</h3>
    ${openGates.length?'<ul>'+openGates.map(i=>`<li><button type="button" class="plain-button" data-inspect-item="${e(i.id)}">${e(i.id)} · ${e(i.title)} →</button></li>`).join('')+'</ul>':'<p>The source records every declared criterion as complete.</p>'}
    ${metGates.length?'<details><summary>'+metGates.length+' previously met criteria</summary><ul>'+metGates.map(i=>'<li>'+e(i.id)+' · '+e(i.title)+'</li>').join('')+'</ul></details>':''}
    ${m.unscopedWork.length?'<h3>Known work without leaf items</h3><ul>'+m.unscopedWork.map(w=>'<li>'+e(w)+'</li>').join('')+'</ul><p>Not included in the percentage until it is scoped into work items.</p>':''}</div>`;
  detail.querySelectorAll('[data-inspect-item]').forEach(button=>button.addEventListener('click',()=>{explorer.selectItem(button.dataset.inspectItem);document.querySelector('[data-pr-close]')?.focus();writeSelection({milestone:id,item:button.dataset.inspectItem});document.querySelector('.pr-detail')?.scrollIntoView({block:'nearest'});}));
  return true;
}
function showMilestone(id,push=true) {
  if(!renderMilestoneDetail(id))return;
  explorer.selectMilestone(id);
  if(push)writeSelection({milestone:id,item:null});
  document.getElementById('explore').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'});
}
document.querySelectorAll('[data-milestone]').forEach(button=>button.addEventListener('click',()=>{showMilestone(button.dataset.milestone);detail.querySelector('[data-milestone-title]')?.focus();}));
document.querySelector('[data-appearance]').addEventListener('click',()=>{
  const dark=document.documentElement.dataset.appearance==='dark'||(!document.documentElement.dataset.appearance&&matchMedia('(prefers-color-scheme:dark)').matches);
  document.documentElement.dataset.appearance=dark?'light':'dark';
});
function restoreSelection(){
  const raw=location.hash.slice(1), parameters=new URLSearchParams(raw);
  const id=parameters.get('m') || (raw.includes('=')?'':decodeURIComponent(raw));
  if(record.milestones.some(m=>m.id===id))showMilestone(id,false);else{explorer.selectMilestone('');detail.innerHTML='';}
  const item=parameters.get('item');
  if(item && record.items.some(i=>i.id===item)){explorer.selectItem(item);document.querySelector('.pr-detail')?.scrollIntoView({block:'nearest'});}
}
addEventListener('popstate',restoreSelection);
if(location.hash)restoreSelection();
'''
    source_url = _source_url(record)
    source_navigation = ('<a href="' + escape(source_url) + '">Canonical source at ' + escape(_source_label(record)) + ' ↗</a>') if source_url else ('Content-addressed source snapshot: ' + escape(record['source']['path']) + ' · ' + escape(_source_label(record)))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>{escape(record['project']['name'])} · source-backed progress reference</title><style>{_theme_css(theme)}:root{{--host-font:{theme['font']}}}{BASE_CSS}{css}</style></head><body class="{project}"><a class="skip-link" href="#top">Skip to tracking</a><div class="review-strip">Reference integration · {escape(mode_note)} · source observed {escape(record['source']['observedOn'])}</div><main class="wrap" id="top" tabindex="-1">{body}<section class="explorer-section" aria-label="History and delivery"><h2 style="margin-bottom:22px">History and delivery</h2><div id="delivery-explorer"></div></section><section id="explore" class="explorer-section"><div class="section-head"><h2>{'Open the workbench' if project == 'prehnite' else 'Inside the work'}</h2><span>Choose a milestone above or explore the ledger below</span></div><p>Find a work item, select its tile, and follow its scope, dependencies and available evidence. These figures come from the source snapshot.</p><div id="milestone-detail"></div><div id="work-explorer" class="pr-host"></div><p class="evidence-notice">Source evidence is retained. The standard does not turn legacy completion labels into a new approval.</p></section><details class="source-detail"><summary>Source, calculation and publication limits</summary><p>{source_navigation} · updated {escape(record['source']['updatedOn'])} · observed {escape(record['source']['observedOn'])}</p><p>Input SHA-256: <code>{record['source']['sha256']}</code></p><p>{escape(record['source']['authority'])}. Percentages count completed leaf items, with each denominator named. Active work earns no partial credit. Accepted milestones follow their declared exit criteria.</p><p>{escape(' '.join(record['warnings']))}</p><p>This is an additive reference integration. The existing website, hero artwork, navigation and authored content are not replaced.</p></details><p class="back-to-top"><a href="#top">Back to top ↑</a></p></main><script type="application/json" id="record-data">{model}</script><script>(()=>{{{script}}})();</script></body></html>'''


def render_readme(record: dict, theme: dict) -> tuple[str, str]:
    """Creates compact branded SVG and text with matching counts."""
    work, accepted = record["metrics"]["work"], record["metrics"]["milestones"]
    roadmap = record["presentation"].get("readmeMetric") == "roadmapMean"
    primary = record["metrics"]["roadmapMean"] if roadmap else work
    primary_label = "Roadmap work" if roadmap else "Required work"
    primary_count = f"Mean across {primary['milestoneCount']} milestones" if roadmap else f"{work['done']} / {work['total']} items"
    primary_text = f"{_percent(primary['percent'])} · {primary_count}" if roadmap else f"{work['done']}/{work['total']} · {_percent(work['percent'])}"
    meaning = "Equal weight for each milestone's required-work fraction." if roadmap else "Completed leaf items in the named required scope."
    title = record["project"]["name"] + (" · roadmap" if roadmap else " · current required scope")
    progress_url = record["presentation"].get("progressUrl") or ("./progress.html" if record["presentation"].get("renderer") != "host" else None)
    image_url = record["presentation"].get("readmeImageUrl", "./progress.svg")
    graphic = f"![{title}]({image_url})"
    if progress_url:
        graphic = f"[{graphic}]({progress_url})"
    source_url = _source_url(record)
    navigation = f"[Interactive roadmap]({progress_url})" if progress_url else "Interactive route not connected."
    source_link = f"[Canonical source]({source_url})" if source_url else f"Source file: `{record['source']['path']}` (content-addressed file snapshot)."
    tokens = theme["light"]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc" viewBox="0 0 840 214"><title id="title">{escape(title)}</title><desc id="desc">Work {work['done']} of {work['total']} ({_percent(work['percent'])}); accepted milestones {accepted['done']} of {accepted['total']} ({_percent(accepted['percent'])}). Observed {record['source']['observedOn']}.</desc><rect width="840" height="214" rx="10" fill="{tokens['background']}"/><g font-family="{escape(theme['font'],quote=True)}" fill="{tokens['text']}"><text x="28" y="37" font-size="18" font-weight="700">{escape(title)}</text><text x="28" y="77" font-size="14">Required work</text><text x="28" y="112" font-size="28" font-weight="700">{_percent(work['percent'])}</text><text x="148" y="111" font-size="14">{work['done']} / {work['total']} items</text><rect x="28" y="132" width="350" height="8" rx="4" fill="{tokens['border']}"/><rect x="28" y="132" width="{350*(work['percent'] or 0)/100:.2f}" height="8" rx="4" fill="{tokens['accent']}"/><text x="445" y="77" font-size="14">Accepted milestones</text><text x="445" y="112" font-size="28" font-weight="700">{_percent(accepted['percent'])}</text><text x="565" y="111" font-size="14">{accepted['done']} / {accepted['total']} outcomes</text><rect x="445" y="132" width="350" height="8" rx="4" fill="{tokens['border']}"/><rect x="445" y="132" width="{350*(accepted['percent'] or 0)/100:.2f}" height="8" rx="4" fill="{tokens['accent']}"/><text x="28" y="181" font-size="12" fill="{tokens['muted']}">Observed {record['source']['observedOn']} · {_source_label(record)} · source-backed snapshot</text></g></svg>'''
    svg = svg.replace(f"Work {work['done']} of {work['total']} ({_percent(work['percent'])})", f"{primary_label} {_percent(primary['percent'])}, {primary_count}")
    svg = svg.replace('>Required work</text>', f'>{primary_label}</text>')
    svg = svg.replace(f">{_percent(work['percent'])}</text>", f">{_percent(primary['percent'])}</text>", 1)
    svg = svg.replace(f">{work['done']} / {work['total']} items</text>", f">{primary_count}</text>", 1)
    svg = svg.replace(f'width="{350*(work["percent"] or 0)/100:.2f}"', f'width="{350*(primary["percent"] or 0)/100:.2f}"', 1)
    md = f'''<!-- project-record:start -->
{graphic}

| Measure | Completion | Meaning |
| --- | ---: | --- |
| {primary_label} | {primary_text} | {meaning} |
| Accepted milestones | {accepted['done']}/{accepted['total']} · {_percent(accepted['percent'])} | Milestones whose declared outcome gates passed. |

{navigation} · {source_link}

Observed {record['source']['observedOn']} against `{_source_label(record)}`.
<!-- project-record:end -->
'''
    return svg, md


def build(records: list[dict], config_path: Path, destination: Path,
          audience: str, toolkit_root: Path) -> list[dict]:
    """Writes deterministic reference files after every audience check passes.

    Args:
        records: The normalized records selected for this build.
        config_path: The configuration path used to resolve project-owned themes.
        destination: The output directory for generated files.
        audience: The requested owner or public audience.
        toolkit_root: The checkout containing shared browser components.

    Returns:
        The build manifest entries with source and output identities.
    """
    ready = [export_record(r, audience) for r in records]
    if audience == "public" and destination.exists() and any(destination.iterdir()):
        raise RecordError("Public build needs a new or empty destination to prevent stale private files")
    manifest = []
    files = {}
    for record in ready:
        project = record["project"]["id"]
        import re
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", project):
            raise RecordError("Project ID must be a safe output-directory name")
        record["deliverySummary"] = delivery_summary(record)
        theme = json.loads((config_path.parent / record["presentation"]["theme"]).read_text())
        own = {"record.json": json.dumps(record, ensure_ascii=False, indent=2) + "\n",
               "history.json": json.dumps(record.get("history", {}), indent=2) + "\n",
               "delivery.json": json.dumps(record["deliverySummary"], indent=2) + "\n",
               "CHANGELOG-generated.md": changelog_markdown(record)}
        renderer = record["presentation"].get("renderer", project)
        if renderer != "host":
            if renderer != project:
                raise RecordError("A reference renderer cannot replace another project's brand")
            own["progress.html"] = render_html(record, theme, toolkit_root)
        svg, md = render_readme(record, theme)
        own.update({"progress.svg": svg, "README-module.md": md})
        hashes = {project + "/" + name: hashlib.sha256(content.encode()).hexdigest() for name, content in own.items()}
        manifest.append({"project": project, "audience": audience, "source": record["source"], "metrics": record["metrics"], "files": list(hashes), "sha256": hashes})
        files.update({project + "/" + name: content for name, content in own.items()})
    files["build-manifest.json"] = json.dumps(manifest, indent=2) + "\n"
    for relative, content in files.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(content)
        temporary.replace(output)
    return manifest
