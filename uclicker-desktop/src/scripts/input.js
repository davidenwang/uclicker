const cleave = new Cleave('#iclicker-id', {
    blocks: [2, 2, 2, 2],
    uppercase: true
});

const navigate = require('./imports').navigate;
const submitButton = document.querySelector('#submitClicker');
submitButton.addEventListener('click', () => {
    navigate('clicker');
})