const botonMenu = document.getElementById("btn-menu");
const fondoMenu = document.getElementById("fondo-menu");

if (botonMenu && fondoMenu) {
    botonMenu.addEventListener("click", () => {
        document.body.classList.toggle("menu-abierto");
    });

    fondoMenu.addEventListener("click", () => {
        document.body.classList.remove("menu-abierto");
    });
}
const gatos = {
    error: [
        "/static/i/6.png",
        "/static/i/7.png",
        "/static/i/8.png",
        "/static/i/9.png",
        "/static/i/10.png"
    ],
    exito: [
        "/static/i/1.1.png",
        "/static/i/1.2.png",
        "/static/i/1.3.png"
    ]
};

function gatoAleatorio(tipo) {
    const lista = gatos[tipo] || gatos.error;
    const ultimo = sessionStorage.getItem("ultimo-gato");
    const opciones = lista.length > 1 ? lista.filter((ruta) => ruta !== ultimo) : lista;
    const elegido = opciones[Math.floor(Math.random() * opciones.length)];
    sessionStorage.setItem("ultimo-gato", elegido);
    document.getElementById("mensaje-icono").src = elegido;
}

function mostrarMensaje(titulo, texto, tipo = "error") {
    gatoAleatorio(tipo);
    document.getElementById("mensaje-titulo").textContent = titulo;
    document.getElementById("mensaje-texto").textContent = texto;
    document.getElementById("mensaje").style.display = "flex";
}

function cerrarMensaje() {
    document.getElementById("mensaje").style.display = "none";
}
function mostrarError(campo, mensaje) {
    const contenedor = campo.closest(".campo") || campo;
    let aviso = contenedor.nextElementSibling;
    const existe = aviso && aviso.classList.contains("error");

    if (!existe && mensaje === "") {
        return;
    }

    if (!existe) {
        aviso = document.createElement("small");
        aviso.className = "error";
        contenedor.after(aviso);
    }

    aviso.textContent = mensaje;
    contenedor.classList.toggle("invalido", mensaje !== "");
}

function limpiarAlEscribir(formulario) {
    formulario.querySelectorAll("input, textarea, select").forEach((campo) => {
        campo.addEventListener("input", () => mostrarError(campo, ""));
    });
}

function validarFormulario(formulario, reglas) {
    formulario.noValidate = true;
    limpiarAlEscribir(formulario);

    formulario.addEventListener("submit", (evento) => {
        let primerError = null;

        reglas.forEach(([id, comprobar]) => {
            const campo = document.getElementById(id);
            const mensaje = comprobar(campo.value.trim());
            mostrarError(campo, mensaje);
            if (mensaje && !primerError) {
                primerError = campo;
            }
        });

        if (primerError) {
            evento.preventDefault();
            primerError.focus();
        }
    });
}

function fechaDeHoy() {
    const ahora = new Date();
    const local = new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
}

const formSesion = document.getElementById("sesion");
if (formSesion) {
    validarFormulario(formSesion, [
        ["usuario", (v) => (v === "" ? "Escribe tu usuario." : "")],
        ["contrasena", (v) => (v === "" ? "Escribe tu contraseña." : "")]
    ]);
}

const formRegistro = document.getElementById("form-registro");
if (formRegistro) {
    validarFormulario(formRegistro, [
        ["reg-usuario", (v) => {
            if (v.length < 3) return "Mínimo 3 caracteres.";
            if (!/^\w+$/.test(v)) return "Solo letras, números y guion bajo.";
            return "";
        }],
        ["reg-contrasena", (v) => (v.length < 6 ? "Mínimo 6 caracteres." : "")],
        ["reg-confirmar", (v) => {
            const clave = document.getElementById("reg-contrasena").value.trim();
            if (v !== clave) {
                mostrarMensaje("¡Ups!", "Las contraseñas no coinciden. Inténtalo de nuevo.");
                return "Las contraseñas no coinciden.";
            }
            return "";
        }]
    ]);
}

const formAccion = document.getElementById("form-accion");
if (formAccion) {
    const hoy = fechaDeHoy();
    const campoFecha = document.getElementById("fecha");
    campoFecha.max = hoy;
    if (!campoFecha.value) {
        campoFecha.value = hoy;
    }

    validarFormulario(formAccion, [
        ["descripcion", (v) => (v.length < 5 ? "Describe tu acción (mínimo 5 caracteres)." : "")],
        ["fecha", (v) => {
            if (v === "") return "Elige una fecha.";
            if (v > hoy) return "La fecha no puede ser futura.";
            return "";
        }],
        ["impacto", (v) => {
            if (v === "") return "Escribe el impacto de tu acción.";
            if (!/\d/.test(v)) return "Incluye una cantidad, ej. 5 kg.";
            return "";
        }]
    ]);
}

function normalizar(texto) {
    return texto.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

const buscador = document.getElementById("buscar");
const tabla = document.getElementById("tabla-acciones");

if (buscador && tabla) {
    const filas = tabla.querySelectorAll("tbody tr");
    const filaVacia = document.createElement("tr");
    filaVacia.innerHTML = '<td colspan="6">No se encontraron acciones.</td>';
    filaVacia.hidden = true;
    tabla.tBodies[0].appendChild(filaVacia);

    buscador.addEventListener("input", () => {
        const texto = normalizar(buscador.value.trim());
        let visibles = 0;

        filas.forEach((fila) => {
            const coincide = normalizar(fila.textContent).includes(texto);
            fila.hidden = !coincide;
            if (coincide) visibles++;
        });

        filaVacia.hidden = visibles > 0;
    });
}

document.querySelectorAll(".btn-eliminar, .btn-rojo").forEach((boton) => {
    boton.addEventListener("click", (evento) => {
        if (!confirm("¿Seguro que quieres eliminar esta acción?")) {
            evento.preventDefault();
        }
    });
});
const mensaje = document.getElementById("mensaje");

if (mensaje) {
    document.getElementById("mensaje-cerrar").addEventListener("click", cerrarMensaje);

    mensaje.addEventListener("click", (evento) => {
        if (evento.target === mensaje) {
            cerrarMensaje();
        }
    });

    document.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape") {
            cerrarMensaje();
        }
    });

    if (mensaje.dataset.texto) {
    const tipo = mensaje.dataset.tipo === "error" ? "error" : "exito";
    mostrarMensaje(tipo === "error" ? "¡Ups!" : "¡Listo!", mensaje.dataset.texto, tipo);
    }
}