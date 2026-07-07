async function cargarEstado() {
    const contenedor = document.getElementById('estado');

    try {
        const respuesta = await fetch('/estado');
        if (!respuesta.ok) {
            contenedor.textContent = 'Error al consultar /estado: ' + respuesta.status;
            return;
        }

        const data = await respuesta.json();
        contenedor.textContent = JSON.stringify(data, null, 2);
    } catch (e) {
        contenedor.textContent = 'Error al conectar con el backend: ' + e.message;
    }
}

cargarEstado();
