let csrf_token = null,
    container = document.querySelector('#ajax-content'),
    pagination = document.querySelector('#ajax-pagination'),
    spinner = document.querySelector('#ajax-spinner');
window.addEventListener('load', () => {loadPage();});

let form = document.querySelector('form#search_form');
form?.addEventListener('submit', (e) => {
    e.preventDefault();
    let formData = new FormData(form);
    setUrlParam('page', 1, true)
    updateUrlSearch(new URLSearchParams(formData));


    loadPage();
    return false;
})

let selects = document.querySelectorAll('select');
for (let select of selects) {
    select.addEventListener('change', (e) => {
        e = new Event('submit')
        form.dispatchEvent(e);
    })
}

function populateSearch(data) {
    let paramsObject = JSON.parse(data),
        searchParams = new URLSearchParams(paramsObject),
        entries = searchParams.entries();
    for(const [key, val] of entries) {
        let element = document.querySelector(`input[name=${key}]`);
        if (element) {
            element.value = val;
        }
    }

    for (let select of selects) {
        for (let option of select.options) {
            if (option.value === searchParams.get(select.getAttribute('name'))) {
                select.options.selectedIndex = option.index;
                break;
            }
        }
        setUrlParam(select.getAttribute('name'), select.options.item(select.options.selectedIndex).value);
    }
}


window.onpopstate = (e) => {
    loadPage(getUrlParam('page'), true)
}


function currentSearchJSON() {
    let currentParams = currentSearch(),
        paramsObject = Object.fromEntries(currentParams.entries())
    return JSON.stringify(paramsObject)
}


function currentSearch() {
    return new URLSearchParams(location.search);
}


// Змінити задані query-параметри (для відтворення сторінки при передачі посилання іншому користувачу)
function setUrlParam(param, value, nopush=false) {
    let searchParams = currentSearch();
    searchParams.set(param, value);
    if (!nopush) {
        window.history.pushState(searchParams.toString(), "", location.pathname + "?" + searchParams.toString());
    }
}


function updateUrlSearch(newURLSearchParams) {
    let oldURLSearchParams = currentSearch(),
        updatedURLSearchParams = new URLSearchParams({
            ...Object.fromEntries(oldURLSearchParams),
            ...Object.fromEntries(newURLSearchParams)
        });
    window.history.pushState(updatedURLSearchParams.toString(), "", location.pathname + "?" + updatedURLSearchParams.toString());
}


function getUrlParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

// TODO: fix spamming history pushes.
function loadPage(page=-1, popstate=false, target=null){
    if (csrf_token === null)
        csrf_token = document.querySelector('meta[name="csrf-token"]').content;
    if (target !== null)
        target.preventDefault();

    window.scrollTo({top: 0, behavior: 'smooth'});
    let request = new XMLHttpRequest();

    if (page === -1){
        page = getUrlParam('page');
        if (!page){
            page = 1;
            setUrlParam('page', page, true);
        }
    }

    request.open('post', '/api' + location.pathname);
    request.setRequestHeader('Content-Type', 'text/html');
    request.setRequestHeader('X-CSRFToken', csrf_token);
    request.setRequestHeader('page', page ? page.toString() : 1 );
    request.setRequestHeader('search', encodeURIComponent(currentSearchJSON()));
    populateSearch(currentSearchJSON());
    request.onload = (e) => {
        spinner.hidden = true;
        let response = JSON.parse(request.response)
        container.innerHTML = response['content'];
        pagination.innerHTML = response['pagination'];
        container.classList.add('animate__fadeIn')
        container.classList.remove('animate__fadeOut')
        try {
            page = +pagination.querySelector('#current_page')?.innerHTML;
            if (isNaN(page)) {
                page = 1;
            }
        }
        catch (e) {
            page = 1;
        }
        if (!popstate)
            setUrlParam('page', page);
    }
    container.classList.remove('animate__fadeIn')
    container.classList.add('animate__fadeOut')
    pagination.innerHTML = '';
    spinner.hidden = false;
    request.send();
}
