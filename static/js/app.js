(() => {
  'use strict';

  const select = document.getElementById('disco-select');
  const title = document.getElementById('album-name');
  const hint = document.getElementById('album-hint');
  const year = document.getElementById('album-year');
  const label = document.getElementById('album-label');
  const state = document.getElementById('query-state');
  const help = document.getElementById('panel-help');
  let controller = null;

  function reset() {
    title.textContent = 'Sin seleccionar';
    hint.textContent = 'Elegí un título para explorar';
    year.textContent = '—';
    label.textContent = '—';
    state.textContent = 'LISTO PARA EXPLORAR';
    help.textContent = 'Los datos se consultan en tiempo real a través de Flask y PostgreSQL.';
  }

  select.addEventListener('change', async () => {
    if (controller) controller.abort();
    const id = select.value;
    if (!id) { reset(); return; }

    const current = new AbortController();
    controller = current;
    title.textContent = select.options[select.selectedIndex].text;
    hint.textContent = 'Consultando el archivo discográfico';
    year.textContent = '…';
    label.textContent = '…';
    state.textContent = 'CONSULTANDO...';
    help.textContent = 'Recuperando datos del disco seleccionado.';

    try {
      const response = await fetch(`${select.dataset.apiBase}${encodeURIComponent(id)}`, {
        signal: current.signal,
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) throw new Error('La consulta no pudo completarse.');
      const data = await response.json();
      if (current !== controller) return;
      year.textContent = String(data.anio);
      label.textContent = data.sello;
      hint.textContent = 'Ficha disponible en el archivo';
      state.textContent = 'CONSULTA COMPLETA';
      help.textContent = 'Datos recuperados mediante obtener_disco() en PostgreSQL.';
    } catch (error) {
      if (error.name === 'AbortError' || current !== controller) return;
      hint.textContent = 'Consulta no disponible';
      year.textContent = '—';
      label.textContent = '—';
      state.textContent = 'ERROR DE CONEXIÓN';
      help.textContent = 'No se pudo consultar el disco. Comprobá la conexión con PostgreSQL.';
    }
  });
})();
