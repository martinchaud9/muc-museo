/* Accesibilidad del sitio del MUC:
   - preferencias visuales (texto grande, alto contraste, colores para daltonismo, sin animaciones)
   - lectura en voz alta con la Web Speech API (speechSynthesis) */
(function () {
  const CLAVE = 'muc-accesibilidad';
  const OPCIONES = ['texto-grande', 'alto-contraste', 'daltonismo', 'sin-animaciones'];
  let prefs = {};
  try { prefs = JSON.parse(localStorage.getItem(CLAVE)) || {}; } catch (e) { /* sin almacenamiento */ }

  const aplicar = () => OPCIONES.forEach(o => document.documentElement.classList.toggle('a11y-' + o, !!prefs[o]));
  aplicar();   // se ejecuta en el <head> para que la página ya se dibuje con las preferencias

  document.addEventListener('DOMContentLoaded', () => {
    const boton = document.getElementById('a11y-boton');
    const panel = document.getElementById('a11y-panel');
    if (!boton || !panel) return;
    const abrir = v => { panel.hidden = !v; boton.setAttribute('aria-expanded', v); };
    boton.addEventListener('click', () => abrir(panel.hidden));
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !panel.hidden) { abrir(false); boton.focus(); } });
    document.addEventListener('click', e => { if (!panel.hidden && !panel.contains(e.target) && !boton.contains(e.target)) abrir(false); });
    panel.querySelectorAll('input[data-opcion]').forEach(inp => {
      inp.checked = !!prefs[inp.dataset.opcion];
      inp.addEventListener('change', () => {
        prefs[inp.dataset.opcion] = inp.checked;
        try { localStorage.setItem(CLAVE, JSON.stringify(prefs)); } catch (e) { /* sin almacenamiento */ }
        aplicar();
        if (inp.checked && window.MUC.registrar) window.MUC.registrar('a11y_opcion', { detalle: inp.dataset.opcion });
      });
    });
  });

  // ---------- Lectura en voz alta ----------
  const synth = window.speechSynthesis;
  const elegirVoz = () => {
    const voces = synth.getVoices().filter(v => v.lang && v.lang.toLowerCase().startsWith('es'));
    const orden = ['es-ar', 'es-419', 'es-mx', 'es-us', 'es-es'];
    for (const l of orden) { const v = voces.find(v => v.lang.toLowerCase().replace('_', '-') === l); if (v) return v; }
    return voces[0] || null;
  };

  window.MUC = Object.assign(window.MUC || {}, {
    puedeLeer: !!synth,
    sinAnimaciones: () => !!prefs['sin-animaciones'] || window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    leyendo: () => !!synth && synth.speaking,
    callar() { if (synth) synth.cancel(); },
    leer(texto, alTerminar) {
      if (!synth) return false;
      synth.cancel();
      const u = new SpeechSynthesisUtterance(texto);
      const voz = elegirVoz();
      if (voz) u.voice = voz;
      u.lang = voz ? voz.lang : 'es-AR';
      u.rate = 0.95;
      u.onend = u.onerror = () => { if (alTerminar) alTerminar(); };
      synth.speak(u);
      return true;
    },
    /* Conecta un botón "Escuchar descripción": alterna entre leer y detener. */
    botonLectura(boton, obtenerTexto, datosEvento) {
      if (!synth) { boton.hidden = true; return; }
      const reposo = () => { boton.textContent = '🔊 Escuchar descripción'; boton.setAttribute('aria-pressed', 'false'); };
      reposo();
      boton.addEventListener('click', () => {
        if (boton.getAttribute('aria-pressed') === 'true') { synth.cancel(); reposo(); return; }
        boton.textContent = '⏹ Detener lectura'; boton.setAttribute('aria-pressed', 'true');
        window.MUC.leer(obtenerTexto(), reposo);
        if (window.MUC.registrar) window.MUC.registrar('a11y_leer', datosEvento ? datosEvento() : {});
      });
      return reposo;
    },
    textoObra: o => [o.titulo, o.autor + (o.anio ? ', ' + o.anio : ''), o.tecnica, o.descripcion].filter(Boolean).join('. '),
  });
  window.addEventListener('pagehide', () => { if (synth) synth.cancel(); });
})();
