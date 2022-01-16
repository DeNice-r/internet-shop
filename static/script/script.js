let spinner = document.querySelector('#ajax-spinner');


alerts = document.querySelectorAll('.alert');
alerts.forEach((elem, index) => {
    setTimeout(() => {
        fade(elem)
    }, 5000 + 2000 * index)
})


function fade(element) {
    let op = 1;  // initial opacity
    let timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.remove();
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 50);
}
