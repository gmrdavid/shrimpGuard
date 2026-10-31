const fs = require('fs');

// Create mock DOM
const elements = {};

function createMockElement(id, tag = 'div') {
    return {
        id,
        tagName: tag.toUpperCase(),
        classList: {
            add: () => {},
            remove: () => {},
            contains: () => false,
            toggle: () => {}
        },
        style: {},
        dataset: {},
        innerHTML: '',
        textContent: '',
        value: '100',
        hidden: false,
        clientWidth: 750,
        clientHeight: 320,
        offsetWidth: 285,
        offsetHeight: 210,
        querySelectorAll: () => [],
        querySelector: () => null,
        getBoundingClientRect: () => ({ left: 50, top: 50, width: 750, height: 320 }),
        getContext: () => ({
            scale: () => {},
            clearRect: () => {},
            beginPath: () => {},
            moveTo: () => {},
            lineTo: () => {},
            stroke: () => {},
            fillText: () => {},
            arc: () => {},
            fill: () => {},
            createLinearGradient: () => ({ addColorStop: () => {} }),
            save: () => {},
            restore: () => {},
            setLineDash: () => {},
        }),
        addEventListener: function(event, handler) {
            this.listeners = this.listeners || {};
            this.listeners[event] = this.listeners[event] || [];
            this.listeners[event].push(handler);
        },
        dispatchEvent: function(event, payload) {
            if (this.listeners && this.listeners[event]) {
                this.listeners[event].forEach(fn => fn(payload));
            }
        }
    };
}

const mockDoc = {
    getElementById: (id) => {
        if (!elements[id]) elements[id] = createMockElement(id);
        return elements[id];
    },
    querySelectorAll: (sel) => {
        return [createMockElement('chip-1'), createMockElement('chip-2')];
    },
    querySelector: (sel) => createMockElement('sel'),
    addEventListener: (event, handler) => {
        if (event === 'DOMContentLoaded') setTimeout(handler, 10);
    },
    body: { style: {} }
};

global.document = mockDoc;
global.window = {
    addEventListener: () => {},
    devicePixelRatio: 1,
    requestAnimationFrame: (cb) => cb()
};
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({ latest: [] }) });

// Read calculators.js
const code = fs.readFileSync('static/js/calculators.js', 'utf8');

try {
    eval(code);
    console.log("calculators.js evaluated successfully without syntax errors.");

    // Fire DOMContentLoaded
    setTimeout(() => {
        try {
            console.log("Testing openGrowthGraphModal...");
            const btn = mockDoc.getElementById('btn-open-growth-chart');
            if (btn.listeners && btn.listeners['click']) {
                btn.listeners['click'].forEach(fn => fn());
                console.log("btn-open-growth-chart clicked!");
            }

            console.log("Testing pointermove on canvas...");
            const canvas = mockDoc.getElementById('growth-trend-chart');
            if (canvas.listeners && canvas.listeners['pointermove']) {
                canvas.listeners['pointermove'].forEach(fn => fn({ clientX: 200, clientY: 150 }));
                console.log("pointermove triggered!");
            }

            const tooltip = mockDoc.getElementById('growth-chart-tooltip');
            console.log("Tooltip hidden state:", tooltip.hidden);
            console.log("Tooltip style.left:", tooltip.style.left);
            console.log("Tooltip style.top:", tooltip.style.top);
            console.log("Tooltip innerHTML snippet:", tooltip.innerHTML ? tooltip.innerHTML.substring(0, 150) : "EMPTY");

            console.log("TEST COMPLETED SUCCESSFULLY!");
        } catch (err) {
            console.error("RUNTIME ERROR during test:", err);
            process.exit(1);
        }
    }, 20);

} catch (e) {
    console.error("Evaluation error:", e);
    process.exit(1);
}
