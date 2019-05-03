let clicker_buttons = document.querySelectorAll('.clicker_button');
for (clicker_button of clicker_buttons) {
    clicker_button.addEventListener('click', (evt) => {
        for (temp_clicker_button of clicker_buttons) {
            temp_clicker_button.className = "clicker_button";
        }
        evt.target.className += " clicked";
        submitAnswer(evt.target.innerText.trim());
    })
}

let ipcRenderer = require('electron').ipcRenderer;
/**
 * Submits an answer to the python server using zerorpc
 * @param {string} answer - the answer to be submitted
 */
function submitAnswer(answer) {
    let id = window.iclickerId;
    ipcRenderer.send('submit-answer', {id, answer});
}