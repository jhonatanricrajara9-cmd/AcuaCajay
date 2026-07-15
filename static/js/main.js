document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  // ---- Widget de WhatsApp con selección de mensaje (todas las páginas) ----
  var waToggle = document.getElementById("whatsappToggle");
  var waPanel = document.getElementById("whatsappPanel");
  var waNumeroEl = document.getElementById("whatsappNumero");

  if (waToggle && waPanel && waNumeroEl) {
    var numero = waNumeroEl.getAttribute("data-numero");
    var appUrl = waNumeroEl.getAttribute("data-app-url");

    var abrirWhatsapp = function (mensaje) {
      var url = "https://wa.me/" + numero + "?text=" + encodeURIComponent(mensaje);
      window.open(url, "_blank", "noopener");
    };

    var cerrarPanel = function () {
      waPanel.setAttribute("hidden", "");
      waToggle.setAttribute("aria-expanded", "false");
    };

    waToggle.addEventListener("click", function () {
      var estaAbierto = !waPanel.hasAttribute("hidden");
      if (estaAbierto) {
        cerrarPanel();
      } else {
        waPanel.removeAttribute("hidden");
        waToggle.setAttribute("aria-expanded", "true");
      }
    });

    document.querySelectorAll(".whatsapp-option[data-msg]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        abrirWhatsapp(btn.getAttribute("data-msg"));
        cerrarPanel();
      });
    });

    var waZonaBtn = document.getElementById("waZonaBtn");
    var waZona = document.getElementById("waZona");
    if (waZonaBtn && waZona) {
      waZonaBtn.addEventListener("click", function () {
        abrirWhatsapp("Hola, le escribo del barrio " + waZona.value + ". Más info: " + appUrl);
        cerrarPanel();
      });
    }

    document.addEventListener("click", function (e) {
      if (!waPanel.contains(e.target) && !waToggle.contains(e.target)) {
        cerrarPanel();
      }
    });
  }

  // ---- Notificaciones en vivo (solo existe en la página Avisos) ----
  var liveList = document.getElementById("liveList");
  if (!liveList) return;

  var emptyMsg = document.getElementById("liveEmpty");
  var MAX_ITEMS = 8;

  function pillClase(estado) {
    if (estado === "normal") return "pill-normal";
    if (estado === "corte") return "pill-corte";
    return "pill-bajo";
  }

  function agregarNotificacion(data) {
    if (emptyMsg) { emptyMsg.remove(); emptyMsg = null; }

    var item = document.createElement("div");
    item.className = "live-item";
    item.innerHTML =
      '<span class="pill ' + pillClase(data.estado) + '">' + data.etiqueta + '</span>' +
      '<span>' + data.mensaje + '</span>' +
      '<time>' + data.hora + '</time>';

    liveList.prepend(item);

    while (liveList.children.length > MAX_ITEMS) {
      liveList.removeChild(liveList.lastChild);
    }
  }

  function consultarNotificacion() {
    fetch("/api/notificaciones")
      .then(function (res) { return res.json(); })
      .then(agregarNotificacion)
      .catch(function () { /* silencioso: solo un prototipo */ });
  }

  consultarNotificacion();
  setInterval(consultarNotificacion, 8000);
});
