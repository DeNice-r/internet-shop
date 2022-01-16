let cartNonempty = document.querySelector('div#cart-nonempty'),
    cartEmpty = document.querySelector('div#cart-empty'),
    ajaxContent = document.querySelector('#ajax-content'),
    cartItems = document.querySelector('tbody#cartItems'),
    mutex = false;


document.addEventListener('load', syncCart);
syncCart()

async function syncCart() {
    if (mutex)
        return
    mutex = true;
    if (cartEmpty) {
        if (ajaxContent.innerHTML === '')
            spinner.hidden = false;
        ajaxContent.classList.toggle('disabled');
        let cart_request = await fetch('/api/cart'),
            cart_ = await cart_request.json();
        if (cart_ === '') {
            mutex = false;
            clearCart();
        }
        else {
            ajaxContent.innerHTML = cart_;
            showCart();
        }
        ajaxContent.classList.toggle('disabled');
        spinner.hidden = true;
    }
    mutex = false
}


function addToCart(product_id) {
    if (mutex)
        return
    mutex = true;
    fetch('/api/cart/add/' + product_id + '/1').then(() => { mutex = false; syncCart(); });

}


function setCartItem(input, product_id) {
    if (mutex)
        return
    mutex = true;
    fetch('/api/cart/set/' + product_id + '/' + input.value).then(() => { mutex = false; syncCart(); });
}


function removeFromCart(product_id) {
    if (mutex)
        return
    mutex = true;
    fetch('/api/cart/del/' + product_id).then(() => { mutex = false; syncCart(); });
}

function removeOneFromCart(product_id) {
    if (mutex)
        return
    mutex = true;
    fetch('/api/cart/del/' + product_id + '/1').then(() => { mutex = false; syncCart(); });
}


function clearCart() {
    if (mutex)
        return
    mutex = true;
    fetch('/api/cart/del').then(() => {
        cartNonempty.hidden = true;
        cartEmpty.hidden = false;
        mutex = false
    })
}


function showCart() {
    cartNonempty.hidden = false;
    cartEmpty.hidden = true;
}