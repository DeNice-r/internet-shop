let pictures_input = document.querySelector('input[name="pictures"]'),
    form = document.querySelector('form'),
    picture_container = document.querySelector('div#picture-container'),
    specs_input = document.querySelector('input[name="specs"]'),
    specs_table = document.querySelector('table'),
    specs_table_tbody = specs_table.querySelector('tbody'),
    // remove_spec_buttons = specs_table_tbody.querySelectorAll('input[type="button"].btn-remove-spec'),
    spec_container = document.querySelector('#specCollapse'),
    pictures, specs;

try {
    pictures = JSON.parse(pictures_input.value);
} catch (e) {
    pictures = [];
}

try {
    specs = JSON.parse(specs_input.value);
} catch (e) {
    specs = {};
}

for (let pic_index in pictures) {
    let img = document.createElement('img'),
        wrapper = document.createElement('div'),
        mask = document.createElement('div');
    img.src = picture_path + pictures[pic_index];
    img.classList.add('w-100');
    mask.style.background = 'rgba(255, 0, 0, 0.5)';
    mask.classList.add('mask');
    wrapper.classList.add('bg-image', 'd-inline-block', 'hover-overlay', 'col-6', 'col-sm-4', 'col-xl-3');
    wrapper.style.cursor = 'pointer';
    wrapper.addEventListener('click', (e) => {
        wrapper.remove();
    });
    wrapper.appendChild(img);
    wrapper.appendChild(mask);
    picture_container.appendChild(wrapper);
}


spec_container.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-remove-spec')) {
        let tr = e.target.closest('tr'),
            key = tr.children[1].textContent;
        delete specs[key];
        tr.remove();
    }
})


form.addEventListener('submit', (e) => {
    let pictures = [];
    if (picture_container) {
        for (let w of picture_container.querySelectorAll('.hover-overlay')) {
            pictures.push(w.querySelector('img').src.split('/').pop());
        }
    }
    pictures_input.value = JSON.stringify(pictures);

    specs_input.value = JSON.stringify(specs);
})


let add_spec_button = document.querySelector('#add-spec-button'),
    add_spec_inputs = [...add_spec_button.parentNode.parentNode.querySelectorAll('input')].slice(0, -1);

add_spec_button.addEventListener('click', add_spec);
function add_spec (e){
    e.preventDefault();
    let all_valid = true;
    for (let i of add_spec_inputs) {
        if (i.value === '') {
            i.classList.add('is-invalid');
            all_valid = false;
        }
        else
            i.classList.remove('is-invalid');
    }
    if (all_valid) {
        let key = add_spec_inputs[0].value,
            value = add_spec_inputs[1].value;

        add_spec_inputs[0].value = '';
        add_spec_inputs[1].value = '';

        specs[key] = value;
        console.log(typeof specs);

        let tr = document.createElement('tr'),
            index_td = document.createElement('td'),
            key_td = document.createElement('td'),
            value_td = document.createElement('td'),
            remove_td = document.createElement('td');


        index_td.textContent = specs_table_tbody.children.length.toString();
        key_td.textContent = key;
        value_td.textContent = value;
        remove_td.innerHTML = '<input type="button" class="form-control btn btn-danger btn-remove-spec" value="❌">';

        tr.appendChild(index_td);
        tr.appendChild(key_td);
        tr.appendChild(value_td);
        tr.appendChild(remove_td);
        specs_table_tbody.insertBefore(tr, add_spec_button.parentNode.parentNode);

        return false;
    }
}

