/* Optional index filtering. Static fragments own navigation and browser history. */
function enhanceInspector(doc) {
  const find = doc.getElementById('find');
  const list = doc.getElementById('artifact-index');
  const status = doc.getElementById('results');
  if (!find || !list || !status) return;
  const update = () => {
    const query = find.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const row of list.children) {
      row.hidden = !row.textContent.toLocaleLowerCase().includes(query);
      if (!row.hidden) count++;
    }
    status.textContent = `${count} matching declared files. Records remain available below.`;
  };
  find.addEventListener('input', update);
  update();
}
if (typeof document !== 'undefined') enhanceInspector(document);
