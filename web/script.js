var steps = 40;
var step = 0;
var char = 0;
var dir = 1;
var stop = false;
var goingTo = 0;

var svg = document.getElementsByTagName('svg')[0];
var img = document.getElementById('main');
var texts = Array.from(document.getElementById('texts').children).reverse();
var formats = Array.from(document.querySelectorAll('#formats li'));
var symbol = formats[0].textContent[0];
var baseFontSize = parseFloat(texts[0].getAttribute('font-size'));

var rotate = 90 / steps;
var scale = (Math.SQRT2 - 1) / steps;
var translate = parseInt(svg.getAttribute('height')) / 2 / steps;
var fontSize = (
    parseFloat(texts[0].getAttribute('font-size'))
    - parseFloat(texts[1].getAttribute('font-size'))
) / steps;
var maxChar = parseInt(formats[formats.length-1].textContent.split(' ')[0].substr(1));

svg.onclick = forward;
svg.addEventListener('contextmenu', backward, false);

for (let format of formats) {
    format.onclick = (e) => {
        let data = e.target.textContent.split(' ');
        let number = parseInt(data[0].substr(1));
        let n = number - char;
        if (n === 0) return;
        if (n < 0) {
            n *= -1;
            let len = n - goingTo;
            for (let i = 0; i < len; i++) {
                backward();
            }
        } else {
            let len = n - goingTo;
            for (let i = 0; i < len; i++) {
                forward();
            }
        }
        goingTo = n;
    }
}

function forward() {
    if (char === maxChar) return;
    dir = 1;
    if (step === steps) step = 0;
    goingTo += 1;
    reset();
    animate();
}
function backward(e) {
    if (e) e.preventDefault();
    if (char === 0) return;
    dir = -1;
    if (step === 0) step = steps;
    goingTo += 1;
    reset();
    animate();
    return false;
}

function animate() {
    step += dir;
    img.setAttribute(
        'transform',
        `rotate(-${step*rotate} ${step*translate} ${step*translate}), scale(${1+step*scale})`
    );
    texts[0].setAttribute('stroke-width', 1 - step * ((Math.SQRT2 - 1)/steps) + 'px');
    texts.forEach((elem, i) => {
        let transform = `rotate(${step*rotate} ${elem.getAttribute('x')} ${elem.getAttribute('y')})`;
        if (i == 0) {
            elem.setAttribute('font-size', baseFontSize - step*fontSize + 'px');
            transform += ' translate(-' + step*(translate/2) + ')';
        }
        elem.setAttribute('transform', transform);
    });
    if (step < steps && step > 0) {
        requestAnimationFrame(animate);
    } else {
        char += dir;
        step = dir === 1 ? 0 : steps;
        goingTo -= 1;
        reset();
    }
}

function reset() {
    texts[0].setAttribute('stroke-width', 1 - step * ((Math.SQRT2 - 1)/steps) + 'px');
    texts.forEach((elem, i) => {
        let transform = `rotate(${step*rotate} ${elem.getAttribute('x')} ${elem.getAttribute('y')})`;
        if (i == 0) {
            elem.setAttribute('font-size', baseFontSize - step*fontSize + 'px');
            transform += ' translate(-' + step*(translate/2) + ')';
        }
        elem.setAttribute('transform', transform);
        elem.textContent = symbol + (i + char - (dir === -1 && i != 0 ? 1 : 0));
    });
    img.setAttribute(
        'transform',
        `rotate(-${step*rotate} ${step*translate} ${step*translate}), scale(${1+step*scale})`
    );
    document.querySelector('.selected').classList.remove('selected');
    formats[char].classList.add('selected');
}
