document.addEventListener("DOMContentLoaded", () => {
    // Cargar componentes
    loadComponent("components/sidebar.html", "sidebar-container");
    loadComponent("components/header.html", "header-container");
    loadComponent("components/footer.html", "footer-container");

    // Cargar vista por defecto
    loadView("inicio");

    // Delegar eventos tras renderizado dinámico
    document.addEventListener("click", function (e) {
        if (e.target.matches('[data-view], [data-view] *')) {
            e.preventDefault();
            const link = e.target.closest("[data-view]");
            const view = link.getAttribute("data-view");
            loadView(view);

            // Marcar activo
            document.querySelectorAll("#sidebar .nav-link").forEach(el => el.classList.remove("active"));
            link.classList.add("active");
        }

        if (e.target.id === "toggleSidebar" || e.target.closest("#toggleSidebar")) {
            const sidebar = document.getElementById("sidebar");
            sidebar.classList.toggle("collapsed");

            const logoExpand = sidebar.querySelector(".logo-expand");
            const logoCollapse = sidebar.querySelector(".logo-collapse");

            if (sidebar.classList.contains("collapsed")) {
                logoExpand?.classList.add("d-none");
                logoCollapse?.classList.remove("d-none");
            } else {
                logoExpand?.classList.remove("d-none");
                logoCollapse?.classList.add("d-none");
            }
        }

        if (e.target.id === "buscarVehiculo") {
            const query = document.getElementById("busquedaVehiculo")?.value.trim();
            const resultado = document.getElementById("resultadoBusqueda");
          
            if (!query) {
              resultado.textContent = 'Introduce unha matrícula ou ID.';
              return;
            }
          
            resultado.textContent = 'Buscando...';
          
            fetch(`http://localhost:5000/api/vehiculos/buscar?termino=${encodeURIComponent(query)}`)
              .then(res => res.json())
              .then(data => {
                if (!data.length) {
                  resultado.textContent = 'Non se atopou ningún vehículo.';
                  return;
                }
          
                const vehiculo = data[0]; // asumimos o primeiro
                resultado.textContent = `Vehículo "${vehiculo.referencia}" localizado.`;
          
                // Obtener posición (simulación o real)
                fetch(`http://localhost:5000/api/vehiculos/${vehiculo.id}/tag`)
                  .then(res => res.json())
                  .then(tag => {
                    if (!tag || !tag.id) {
                      resultado.textContent += ' Sen tag asignado.';
                      return;
                    }
          
                    fetch(`http://localhost:5000/api/posiciones/tag/${tag.id}/ultima`)
                      .then(res => res.json())
                      .then(pos => {
                        const svg = document.getElementById("plano-taller");
                        svg.querySelector("#marcador-vehiculo")?.remove();
          
                        const marcador = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                        marcador.setAttribute("cx", pos.x);
                        marcador.setAttribute("cy", pos.y);
                        marcador.setAttribute("r", 10);
                        marcador.setAttribute("fill", "#ff8500");
                        marcador.setAttribute("stroke", "#000");
                        marcador.setAttribute("stroke-width", "1");
                        marcador.setAttribute("id", "marcador-vehiculo");
                        svg.appendChild(marcador);
                      });
                  });
              })
              .catch(() => {
                resultado.textContent = 'Erro na busca.';
              });
          }
    });
});

function loadComponent(url, containerId) {
    fetch(url)
        .then(res => res.text())
        .then(html => {
            document.getElementById(containerId).innerHTML = html;
        });
}

function loadView(view) {
    fetch(`views/${view}.html`)
        .then(res => res.text())
        .then(html => {
            document.getElementById("main-content").innerHTML = html;
        });
}
