(function () {
  var formulario = document.getElementById("formulario-prediccion");
  if (!formulario) {
    return;
  }

  document.querySelectorAll(".boton-ejemplo").forEach(function (boton) {
    boton.addEventListener("click", function () {
      formulario.elements.fiebre.value = boton.getAttribute("data-fiebre");
      formulario.elements.intensidad_dolor.value = boton.getAttribute("data-dolor");
      formulario.elements.dias_sintomas.value = boton.getAttribute("data-dias");
      formulario.elements.numero_sintomas.value = boton.getAttribute("data-sintomas");
      if (typeof formulario.requestSubmit === "function") {
        formulario.requestSubmit();
      } else {
        formulario.submit();
      }
    });
  });

  var aviso = document.querySelector("[role='alert']");
  var resultado = document.querySelector(".resultado");
  var destino = aviso || resultado;
  if (destino) {
    destino.setAttribute("tabindex", "-1");
    destino.focus();
  }
})();
