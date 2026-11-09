/* Analítica propia del MUC: registra visitas y acciones de forma anónima.
   - El visitante se identifica con un código aleatorio guardado en su navegador (sin nombre, correo ni cookies de terceros).
   - Respeta «No rastrear» (Do Not Track / Global Privacy Control): en ese caso no envía nada. */
(function () {
  const script = document.currentScript;
  const URL_EVENTOS = script && script.dataset.url;
  window.MUC = window.MUC || {};
  const noRastrear = navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true;

  const leer = (almacen, clave) => { try { return window[almacen].getItem(clave); } catch (e) { return null; } };
  const guardar = (almacen, clave, valor) => { try { window[almacen].setItem(clave, valor); } catch (e) { /* sin almacenamiento */ } };
  const nuevoCodigo = () => (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
    : Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 12);

  let visitante = leer('localStorage', 'muc-visitante');
  if (!visitante) { visitante = nuevoCodigo(); guardar('localStorage', 'muc-visitante', visitante); }
  let sesion = leer('sessionStorage', 'muc-sesion');
  if (!sesion) { sesion = nuevoCodigo(); guardar('sessionStorage', 'muc-sesion', sesion); }

  // Origen de la sesión: la etiqueta ?origen=… del link (QR, Instagram…) o, si no hay, el sitio del que viene.
  function deducirOrigen() {
    let host = '';
    try { host = document.referrer ? new URL(document.referrer).hostname : ''; } catch (e) { /* referrer inválido */ }
    if (!host || host === location.hostname) return 'directo';
    if (/instagram\./.test(host)) return 'instagram';
    if (/whatsapp\./.test(host)) return 'whatsapp';
    if (/(facebook\.|fb\.)/.test(host)) return 'facebook';
    if (/(^|\.)(t\.co|twitter\.com|x\.com)$/.test(host)) return 'x';
    if (/(google\.|bing\.|duckduckgo\.|yahoo\.)/.test(host)) return 'google';
    return 'otro-sitio';
  }
  const params = new URLSearchParams(location.search);
  let origen = leer('sessionStorage', 'muc-origen');
  if (!origen) {
    const etiqueta = (params.get('origen') || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 30);
    origen = etiqueta || deducirOrigen();
    guardar('sessionStorage', 'muc-origen', origen);
  }
  // Se quita la etiqueta de la barra de direcciones para que no se copie al compartir el link.
  if (params.has('origen')) {
    params.delete('origen');
    const q = params.toString();
    history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash);
  }

  window.MUC.registrar = function (tipo, datos) {
    if (noRastrear || !URL_EVENTOS) return;
    const cuerpo = JSON.stringify(Object.assign({ tipo, visitante, sesion, origen, ruta: location.pathname }, datos || {}));
    const blob = new Blob([cuerpo], { type: 'application/json' });
    if (!(navigator.sendBeacon && navigator.sendBeacon(URL_EVENTOS, blob))) {
      fetch(URL_EVENTOS, { method: 'POST', body: cuerpo, headers: { 'Content-Type': 'application/json' }, keepalive: true }).catch(() => {});
    }
  };

  window.MUC.registrar('pagina');
})();
