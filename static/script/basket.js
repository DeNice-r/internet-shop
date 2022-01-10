let basket = null; syncBasket(),
    basketItems = document.querySelector('tbody#basketItems'),
    basketNumber = document.querySelector('#basketNumber');

document.addEventListener('load', syncBasket);


function syncBasket() {
    if (basket === null)
        try {
            basket = JSON.parse(getCookie('basket'));
        } catch (e) {
            basket = {}
        }
    document.cookie = 'basket=' + JSON.stringify(basket) + '; path=/;';
    let sum = 0;
    try {
        let basketList = basketItems.querySelectorAll('.local-sum');
        for (let elem of basketList) {
            sum += +elem.textContent.slice(1);
        }
        document.querySelector('#overall-sum').textContent = '₴' + sum.toFixed(2);
    } catch (e) {}
    let len = Object.entries(basket).length;
    try {
        if (len > 0)
            basketNumber.innerHTML = '(' + len + ')';
        else
            basketNumber.innerHTML = '';
    } catch (e) {}
}


function addToBasket(product_id) {
    if (product_id in basket) {
        basket[product_id] += 1;
        if (basketItems)
            basketItems.querySelector(`tr[product-id="${product_id}"]`)
                .querySelector('input[type="text"]').value = basket[product_id];
    }
    else {
        basket[product_id] = 1;
    }
    syncBasket();
}


function setBasketItem(input, product_id) {
    try {
        if (+input.value > input.max) {
            basket[product_id] = input.max;
            input.value = input.max;
        }
        else
            basket[product_id] = parseInt(input.value);
        let p = basketItems.querySelector(`tr[product-id="${product_id}"]`)
        p.querySelector('.local-sum').textContent = '₴' + (input.value * p.getAttribute('product-price')).toFixed(2);
    } catch (e) {}
    if (basket[product_id] <= 0) {
        return removeFromBasket(product_id);
    }
    syncBasket();
}


// function removeOneFromBasket(product_id) {
//     if (product_id in basket) {
//         basket[product_id] -= 1;
//         if (basket[product_id] === 0) {
//             return removeFromBasket(product_id);
//         }
//         basketItems.querySelector(`tr[product-id="${product_id}"]`)
//             .querySelector('input[type="text"]').value = basket[product_id];
//     }
//     syncBasket();
// }


function removeFromBasket(product_id) {
    delete basket[product_id];
    try {
        basketItems.querySelector(`tr[product-id="${product_id}"]`).remove();
    }
    catch (e) {}
    if (!basketItems.querySelector('tr')) {

        document.querySelector('div#basket-nonempty').hidden = true;
        document.querySelector('div#basket-empty').hidden = false;
    }
    syncBasket();
}


function clearBasket() {
    basket = {};
    document.querySelector('div#basket-nonempty').hidden = true;
    document.querySelector('div#basket-empty').hidden = false;
    syncBasket();
}


function getCookie(name) {
    let matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}
