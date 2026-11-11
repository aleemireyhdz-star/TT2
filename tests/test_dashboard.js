const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function dashboard(fetch) {
    const elements = new Map();
    const element = id => {
        if (!elements.has(id)) elements.set(id, {
            textContent: '', innerHTML: '',
            classList: { add() {}, remove() {} }
        });
        return elements.get(id);
    };
    const context = vm.createContext({
        document: { addEventListener() {}, getElementById: element, querySelector: element },
        fetch, console: { error() {}, warn() {} }
    });
    vm.runInContext(fs.readFileSync(path.join(__dirname, '../src/static/app.js'), 'utf8'), context);
    vm.runInContext('marker = {setLatLng() {}, bindPopup() {}}; map = {hasBeenCentered: true};', context);
    return { context, element };
}

const reading = {
    alerta: 'VERDE', riesgo_zona: 'BAJO', riesgo_score: 0, nivel_sensor: 0,
    coordenadas: {latitud: 19.5, longitud: -99.1},
    received_at: '2026-10-20T12:15:33+00:00', data_status: 'fresh'
};

test('shows the sample timestamp and preserves a numeric zero', () => {
    const {context, element} = dashboard();
    context.actualizarUI(reading);
    assert.equal(element('last-update').textContent,
        new Date(reading.received_at).toLocaleTimeString('es-MX', {
            hour:'2-digit', minute:'2-digit', second:'2-digit'
        }));
    assert.equal(element('riesgo-score').textContent, 0);
    context.actualizarUI({...reading});
    assert.equal(element('last-update').textContent,
        new Date(reading.received_at).toLocaleTimeString('es-MX', {
            hour:'2-digit', minute:'2-digit', second:'2-digit'
        }));
});

test('waiting and stale messages use server state rather than polling time', () => {
    const {context, element} = dashboard();
    context.actualizarUI({...reading, alerta:'GRIS', received_at:null,
        mensaje:'Esperando datos del sensor...'});
    assert.equal(element('last-update').textContent, '--');
    assert.equal(element('alerta-description').textContent, 'Esperando datos del sensor...');
    context.actualizarUI({...reading, alerta:'GRIS', data_status:'stale',
        mensaje:'Sin recepción reciente del sensor.'});
    assert.equal(element('alerta-label').textContent, 'GRIS');
    assert.equal(element('alerta-description').textContent, 'Sin recepción reciente del sensor.');
});

test('HTTP failures do not update the UI or report a server connection', async () => {
    const {context, element} = dashboard(async () => ({ok:false, status:500}));
    element('last-update').textContent = 'previous reading';
    await context.actualizarEstado();
    assert.equal(element('status-text').textContent, 'Sin conexión al servidor');
    assert.equal(element('last-update').textContent, 'previous reading');
});
