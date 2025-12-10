// Variables globales
let map;
let marker;
let historialEventos = [];
const MAX_HISTORIAL = 50;

// Emojis para diferentes estados
const emojis = {
    VERDE: '🟢',
    AMARILLO: '🟡',
    ROJO: '🔴'
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    inicializarMapa();
    inicializarActualizaciones();
    setupCoordsForm();
    fetchCoords();
});

// Inicializar el mapa con Leaflet
function inicializarMapa() {
    // Coordenadas por defecto: CDMX Centro
    const coordInicial = [19.4326, -99.1332];
    
    map = L.map('map').setView(coordInicial, 13);
    
    // Agregar tiles del mapa
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Crear marcador
    marker = L.marker(coordInicial, {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).addTo(map);
    
    // Hacer ping inicial para obtener datos
    actualizarEstado();
}

// Actualizar estado cada 2 segundos
function inicializarActualizaciones() {
    actualizarEstado();
    setInterval(actualizarEstado, 2000);
}

// Actualizar el estado de la predicción
async function actualizarEstado() {
    try {
        const response = await fetch('/api/status');
        const datos = await response.json();
        
        // Actualizar elementos en la página
        actualizarUI(datos);
        
        // Actualizar mapa
        if (datos.coordenadas) {
            actualizarMapa(datos.coordenadas);
        }
        
        // Actualizar estado de conexión
        actualizarEstadoConexion('online');
    } catch (error) {
        console.error('Error al obtener estado:', error);
        actualizarEstadoConexion('offline');
    }
}

// Actualizar elementos de la interfaz
function actualizarUI(datos) {
    const { alerta, riesgo_zona, riesgo_score, nivel_sensor, coordenadas, mensaje } = datos;
    
    // Actualizar coordenadas
    if (coordenadas) {
        document.getElementById('lat').textContent = coordenadas.latitud.toFixed(6);
        document.getElementById('lon').textContent = coordenadas.longitud.toFixed(6);
    }
    
    // Actualizar nivel del sensor
    if (nivel_sensor !== undefined && nivel_sensor >= 0) {
        document.getElementById('nivel-sensor').textContent = nivel_sensor;
    } else {
        document.getElementById('nivel-sensor').textContent = '-';
    }
    
    // Actualizar riesgo de zona
    document.getElementById('riesgo-zona').textContent = riesgo_zona || '--';
    document.getElementById('riesgo-score').textContent = riesgo_score || '--';
    
    // Actualizar semáforo
    actualizarSemaforoAlerta(alerta);
    
    // Actualizar última actualización
    actualizarHoraUltActualizacion();
    
    // Agregar evento al historial si hay cambio
    agregarAlHistorial(alerta, nivel_sensor, riesgo_zona, riesgo_score);
}

// Actualizar el semáforo de alerta
function actualizarSemaforoAlerta(alerta) {
    const circulo = document.querySelector('.circulo');
    const label = document.getElementById('alerta-label');
    const description = document.getElementById('alerta-description');
    
    // Limpiar clases anteriores
    circulo.classList.remove('verde', 'amarillo', 'rojo', 'gris');
    
    // Aplicar clase nueva
    let claseColor = alerta.toLowerCase();
    if (claseColor === 'gris') {
        circulo.classList.add('gris');
    } else {
        circulo.classList.add(claseColor);
    }
    
    // Actualizar etiqueta
    label.textContent = alerta;
    
    // Actualizar descripción
    const descripciones = {
        'VERDE': '✅ Condiciones normales - No se requiere acción',
        'AMARILLO': '⚠️ Precaución - Monitoreo continuo recomendado',
        'ROJO': '🚨 Peligro - Tomar medidas de seguridad inmediatas',
        'GRIS': '⏳ Esperando datos...'
    };
    
    description.textContent = descripciones[alerta] || 'Estado desconocido';
}

// Actualizar mapa con nueva posición
function actualizarMapa(coordenadas) {
    const latlng = [coordenadas.latitud, coordenadas.longitud];
    
    // Actualizar posición del marcador
    marker.setLatLng(latlng);
    
    // Centrar el mapa (solo si es la primera actualización)
    if (!map.hasBeenCentered) {
        map.setView(latlng, 13);
        map.hasBeenCentered = true;
    }
    
    // Actualizar popup del marcador
    const popupText = `
        <strong>Ubicación del Sensor</strong><br>
        Lat: ${coordenadas.latitud.toFixed(6)}<br>
        Lon: ${coordenadas.longitud.toFixed(6)}
    `;
    marker.bindPopup(popupText);
}

// Agregar evento al historial
function agregarAlHistorial(alerta, nivel_sensor, riesgo_zona, riesgo_score) {
    const ahora = new Date();
    const tiempo = ahora.toLocaleTimeString('es-MX', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    // Evitar duplicados consecutivos
    if (historialEventos.length > 0) {
        const ultimoEvento = historialEventos[0];
        if (ultimoEvento.alerta === alerta && 
            ultimoEvento.nivel_sensor === nivel_sensor) {
            return;
        }
    }
    
    const evento = {
        tiempo,
        alerta,
        nivel_sensor,
        riesgo_zona,
        riesgo_score,
        timestamp: ahora.getTime()
    };
    
    historialEventos.unshift(evento);
    
    // Limitar el historial
    if (historialEventos.length > MAX_HISTORIAL) {
        historialEventos = historialEventos.slice(0, MAX_HISTORIAL);
    }
    
    // Actualizar vista del historial
    actualizarVistaHistorial();
}

// Actualizar vista del historial
function actualizarVistaHistorial() {
    const contenedor = document.getElementById('historial');
    
    if (historialEventos.length === 0) {
        contenedor.innerHTML = '<p class="empty-state">No hay eventos registrados aún...</p>';
        return;
    }
    
    let html = '';
    for (const evento of historialEventos) {
        const emoji = emojis[evento.alerta] || '⚪';
        const claseColor = evento.alerta.toLowerCase();
        
        html += `
            <div class="evento">
                <span class="evento-time">${evento.tiempo}</span>
                <span class="evento-text">
                    ${emoji} Alerta ${evento.alerta} | 
                    Sensor: ${evento.nivel_sensor} | 
                    Riesgo: ${evento.riesgo_zona} (${evento.riesgo_score})
                </span>
                <span class="evento-level ${claseColor}">${evento.alerta}</span>
            </div>
        `;
    }
    
    contenedor.innerHTML = html;
}

// Actualizar hora de última actualización
function actualizarHoraUltActualizacion() {
    const ahora = new Date();
    const tiempo = ahora.toLocaleTimeString('es-MX', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    
    document.getElementById('last-update').textContent = tiempo;
}

// Actualizar estado de conexión
function actualizarEstadoConexion(estado) {
    const statusIndicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (estado === 'online') {
        statusIndicator.classList.remove('offline');
        statusIndicator.classList.add('online');
        statusText.textContent = 'En línea';
    } else {
        statusIndicator.classList.remove('online');
        statusIndicator.classList.add('offline');
        statusText.textContent = 'Sin conexión';
    }
}

// Mostrar notificaciones (opcional, para navegadores que lo soporten)
function mostrarNotificacion(titulo, opciones) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(titulo, opciones);
    }
}

// Obtener coordenadas guardadas en el servidor y actualizar inputs/mapa
async function fetchCoords() {
    try {
        const resp = await fetch('/api/coords');
        if (!resp.ok) return;
        const coords = await resp.json();
        const latEl = document.getElementById('input-lat');
        const lonEl = document.getElementById('input-lon');
        if (latEl && lonEl && coords) {
            latEl.value = coords.latitud;
            lonEl.value = coords.longitud;
            // Actualizar UI y mapa con las coordenadas actuales
            document.getElementById('lat').textContent = coords.latitud.toFixed(6);
            document.getElementById('lon').textContent = coords.longitud.toFixed(6);
            actualizarMapa(coords);
        }
    } catch (err) {
        console.warn('No se pudieron obtener coordenadas:', err);
    }
}

// Configurar el formulario de coordenadas y guardar en servidor
function setupCoordsForm() {
    const btn = document.getElementById('save-coords');
    if (!btn) return;

    btn.addEventListener('click', async (ev) => {
        ev.preventDefault();
        const latEl = document.getElementById('input-lat');
        const lonEl = document.getElementById('input-lon');
        const msg = document.getElementById('coords-message');
        const lat = parseFloat(latEl.value);
        const lon = parseFloat(lonEl.value);

        if (!isFinite(lat) || !isFinite(lon)) {
            msg.textContent = 'Latitud/Longitud inválidas';
            return;
        }

        try {
            const resp = await fetch('/api/coords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lon })
            });
            const data = await resp.json();
            if (resp.ok && data.ok) {
                msg.textContent = 'Coordenadas guardadas correctamente';
                setTimeout(() => { msg.textContent = ''; }, 3000);

                // Actualizar UI local y pedir nuevo estado
                const coords = { latitud: lat, longitud: lon };
                document.getElementById('lat').textContent = lat.toFixed(6);
                document.getElementById('lon').textContent = lon.toFixed(6);
                actualizarMapa(coords);
                actualizarEstado();
            } else {
                msg.textContent = data.error || 'Error al guardar coordenadas';
            }
        } catch (err) {
            console.error(err);
            msg.textContent = 'Error de red al guardar coordenadas';
        }
    });
}
