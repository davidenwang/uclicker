let ipcRenderer = require('electron').ipcRenderer;

function sendId(event) {
    let id = document.getElementById("iclicker-id").value;
    ipcRenderer.send('submit-id', id);
}
