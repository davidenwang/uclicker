const cleave = new Cleave('#iclicker-id', {
    blocks: [2, 2, 2, 2],
    uppercase: true
});


// all the characters that could be in an iclicker ID
const ID_SET = "ABCDEF0123456789"
function isValidId(iclickerId) {
    if (iclickerId.length != 8) {
        return false;
    }
    for(character of iclickerId) {
        if (!ID_SET.includes(character)) {
            return false;
        }
    }
    return true;
}

/**
 * generates a random i clicker id
 */
function generateRandomId() {
    let id = "";
    const bytes = []
    for(let i = 0; i < 3; i++) {
        let randByte = Math.floor(Math.random() * 256);
        bytes.push(randByte);
        id += randByte.toString(16).padStart(2, "0");
        id += " ";
    }
    const lastByte = bytes[0] ^ bytes[1] ^ bytes[2]
    id += lastByte.toString(16).padStart(2, "0");
    return id.toUpperCase();
}

const generateId = document.querySelector('#generateId');
generateId.addEventListener('click', () => {
    let iclickerInput = document.querySelector('#iclicker-id');
    iclickerInput.value = generateRandomId();
});

const navigate = require('./imports').navigate;
const submitButton = document.querySelector('#submitClicker');
// when submit is clicked, navigate to the next page
submitButton.addEventListener('click', () => {
    let idVal = document.querySelector('#iclicker-id').value;
    idVal = idVal.replace(/ /g, "");
    if (isValidId(idVal)) {
        window.iclickerId = idVal;
        navigate('clicker');
    } else {
        alert("Please Enter Valid iClicker ID");
    }
})