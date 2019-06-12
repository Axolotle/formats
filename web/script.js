var steps = 30;
var step = 1;
var char = 0;

var svg = document.getElementsByTagName('svg')[0];
var img = document.getElementById('main');
var texts = Array.from(document.getElementById('texts').children).reverse();

var rotate = 90 / steps;
var scale = (Math.SQRT2 - 1) / steps;
var translate = parseInt(svg.getAttribute('height')) / 2 / steps;
var fontSize = (
    parseFloat(texts[0].getAttribute('font-size'))
    - parseFloat(texts[1].getAttribute('font-size'))
) / steps;

svg.onclick = animate;

function animate() {
    img.setAttribute(
        'transform',
        `rotate(-${step*rotate} ${step*translate} ${step*translate}), scale(${1+step*scale})`
    );
    texts.forEach((elem, i) => {
        let transform = `rotate(${step*rotate} ${elem.getAttribute('x')} ${elem.getAttribute('y')})`;
        if (i == 0) {
            elem.setAttribute('font-size', 66.744 - step*fontSize + 'px');
            transform += ' translate(-' + step*(translate/2) + ')';
        }
        elem.setAttribute('transform', transform);
    });
    if (step++ < steps) {
        requestAnimationFrame(animate);
    } else {
        char++;
        step = 1;
        texts.forEach((elem, i) => {
            if (i == 0) {
                elem.setAttribute('font-size', '66.744px');
            }
            elem.textContent = 'Γ' + (i + char);
            elem.removeAttribute('transform');
        });
        img.removeAttribute('transform');
        // requestAnimationFrame(animate);
    }
}
