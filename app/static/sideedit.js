// static/script.js

let socket = io(`${server_local}/watch`);
let currentFilename = null;

// Limpiar y ejecutar nuevo script
function loadAndExecuteJS(filename) {
    // 1. Eliminar script anterior si existe
    const oldScript = document.getElementById('live-script');
    if (oldScript) oldScript.remove();

    // 2. Crear nuevo script dinámico
    const script = document.createElement('script');
    script.id = 'live-script';
    script.type = 'text/javascript'; // 'text/javascript' o 'module'
    script.src = `${server_local}/read_js?name=${encodeURIComponent(filename)}`;
    script.onload = () => {
        updateStatus(`Script ${filename} cargado y ejecutado.`);
        logMessage(`Ejecutado: ${filename} (${new Date().toLocaleTimeString()})`);
    };
    script.onerror = () => {
        updateStatus(`❌ Error al cargar ${filename}`);
    };
    document.head.appendChild(script);
}

function setWatchFile(filename) {
    filename = filename.trim();
    if (!filename) {
        console.error('Ingresa un nombre de archivo (ej: livecode.js)');
        return;
    }
    if (!filename.endsWith('.js')) {
        console.error('El archivo debe terminar en .js');
        return;
    }
    socket.emit('set_watch_file', { filename: filename });
}

socket.on('connect', () => {
    updateStatus('Conectado al servidor');
});

socket.on('watch_started', (data) => {
    currentFilename = data.filename;
    updateStatus(`Vigilando: ${currentFilename}`);
    loadAndExecuteJS(currentFilename);
});

socket.on('file_changed', () => {
    if (currentFilename) {
        updateStatus(`Archivo modificado: recargando ${currentFilename}...`);
        setTimeout(() => {
            loadAndExecuteJS(currentFilename);
        }, 50);
    }
});

socket.on('file_error', (data) => {
    updateStatus(`${data.message}`);
    currentFilename = null;
});

function updateStatus(msg) {
    console.info('Estado: ' + msg);
}

function logMessage(msg) {
    console.log(msg);
}
