const imports = document.querySelectorAll('link[rel="import"]');

const pages = {}
let currentPage = '';
const FIRST_PAGE = 'get-started';

/**
 * Loads all template pages found in this HTML doc and inserts it inside
 * a .content node
 */
const loadImports = () => {
    for (let link of imports) {
        // grab and clone the template
        let template = link.import.querySelector('template');
        let clone = document.importNode(template.content, true);

        // save the template for navigation
        const pageId = template.id;
        let div = clone.firstElementChild;
        pages[pageId] = div

        document.querySelector('.content').appendChild(clone);
    }

    // let navigationButtons = document.querySelectorAll('.navigate');
    // for (let button of navigationButtons) {
    //     console.log(button);
    //     console.log(button.dataset.page);
    //     button.addEventListener('click', (e) => {
    //         navigate('clicker');
    //     });
    // }
    navigate(FIRST_PAGE)
}

/**
 * Hides the current page and shows the pageId that is specified
 * @param {The id of the page to be shown} pageId 
 */
const navigate = (pageId) => {
    let nextPage = pages[pageId];
    if (nextPage) {
        // hide current div
        let currentDiv = pages[currentPage];
        if (currentDiv) {
            currentDiv.classList.remove('is_shown')
        }
        nextPage.classList.add('is_shown');
        currentPage = pageId;
        // TEST CODE FOR TRANSITIONS
        // setTimeout(() => {
        //     nextPage.classList.remove('is_shown');   
        //     setTimeout(() => {
        //         nextPage.classList.add('is_shown');
        //     }, 500);
        // }, 500);
    }
}

module.exports = {
    navigate
}

loadImports();