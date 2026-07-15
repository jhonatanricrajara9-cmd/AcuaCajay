(function(){
	'use strict';

	const getEstadoEl = () => document.getElementById('estado');
	const defaultHtml = '🟢 El sistema funciona correctamente.';

	function updateEstado({ html = defaultHtml, level = 'success' } = {}){
		const el = getEstadoEl();
		if(!el) return;
		el.className = `alert ${level === 'danger' ? 'alert-danger' : 'alert-success'}`;
		el.innerHTML = html;
		// Move focus for screen readers to notice the update (if appropriate)
		if(typeof el.focus === 'function') el.focus();
	}

	function tuberiaRota(){
		updateEstado({
			level: 'danger',
			html: `🚨 Se detectó una posible tubería rota.<br><br>📍 Ubicación: Sector A<br><br>⚠️ Recomendación: Realizar mantenimiento inmediato.`
		});
		console.info('Simulación: tubería rota');
	}

	function todoBien(){
		updateEstado({ level: 'success', html: defaultHtml });
		console.info('Simulación: todo bien');
	}

	// Backwards compatibility: expose functions globally and under a namespace
	window.Sim = window.Sim || {};
	window.Sim.tuberiaRota = tuberiaRota;
	window.Sim.todoBien = todoBien;
	window.tuberiaRota = tuberiaRota;
	window.todoBien = todoBien;

})();