const imports = document.querySelectorAll('link[rel="import"]');

for (let link of imports) {
    let template = link.import;
    let clone = document.importNode(template, true);
    document.querySelector('.content').appendChild(clone);
}