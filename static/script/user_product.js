let carousel = document.querySelector('#carouselPhoto'),
    productPhotoIndicators = document.querySelector('#productPhotoIndicators').querySelectorAll('li');


for (let indicator in productPhotoIndicators) {
    if (indicator >= 5) {
        console.log(indicator)
        productPhotoIndicators[indicator].hidden = true;
    }
}


carousel.addEventListener('slide.bs.carousel', (e) => {
    console.log(e.to);
    if (e.to === 0) {
        for (let indicator in productPhotoIndicators) {
            productPhotoIndicators[indicator].hidden = indicator >= 5;
        }
    }
    else if (e.to === productPhotoIndicators.length - 1) {
        for (let indicator in productPhotoIndicators) {
            productPhotoIndicators[indicator].hidden = indicator < productPhotoIndicators.length - 5;
        }
    }
    else if (e.to >= 2 && e.to < productPhotoIndicators.length - 2) {
        for (let indicator in productPhotoIndicators) {
            productPhotoIndicators[indicator].hidden = indicator < e.to - 2 || indicator > e.to + 2;
        }
    }
})
