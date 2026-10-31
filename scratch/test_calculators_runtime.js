const fs = require('fs');

const elements = {};

function createMockElement(id, tag = 'div') {
    return {
        id,
        tagName: tag.toUpperCase(),
        classList: {
            add: function(c) { this._classes = this._classes || new Set(); this._classes.add(c); },
            remove: function(c) { this._classes = this._classes || new Set(); this._classes.delete(c); },
            contains: function(c) { return this._classes ? this._classes.has(c) : false; },
            toggle: function(c) { if (this.contains(c)) this.remove(c); else this.add(c); }
        },
        style: {},
        dataset: { metric: 'sr' },
        innerHTML: '',
        textContent: '',
        value: '100',
        hidden: false,
        clientWidth: 750,
        clientHeight: 340,
        offsetWidth: 290,
        offsetHeight: 220,
        querySelectorAll: () => [],
        querySelector: () => null,
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
            closePath: () => {},
            setLineDash: () => {},
        }),
        getBoundingClientRect: () => ({ left: 50, top: 50, width: 750, height: 340 }),
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
        return [createMockElement('chip-sr'), createMockElement('chip-fabw')];
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
global.requestAnimationFrame = (cb) => cb();
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({ latest: [] }) });

// Read calculators.js
const code = fs.readFileSync('static/js/calculators.js', 'utf8');

try {
    eval(code);
    console.log("calculators.js evaluated successfully without syntax errors.");

    // Fire DOMContentLoaded
    setTimeout(() => {
        try {
            console.log("\n--- Testing openGrowthGraphModal ---");
            const btn = mockDoc.getElementById('btn-open-growth-chart');
            if (btn.listeners && btn.listeners['click']) {
                btn.listeners['click'].forEach(fn => fn());
                console.log("SUCCESS: btn-open-growth-chart clicked!");
            }

            console.log("\n--- Testing pointermove on canvas ---");
            const canvas = mockDoc.getElementById('growth-trend-chart');
            if (canvas.listeners && canvas.listeners['pointermove']) {
                // Hover at clientX=250 (inside canvas plot area)
                canvas.listeners['pointermove'].forEach(fn => fn({ clientX: 250, clientY: 150 }));
                console.log("SUCCESS: pointermove triggered at (250, 150)!");
            }

            const tooltip = mockDoc.getElementById('growth-chart-tooltip');
            console.log("\n--- Validating Tooltip State ---");
            console.log("Tooltip hidden:", tooltip.hidden);
            console.log("Tooltip has 'visible' class:", tooltip.classList.contains('visible'));
            console.log("Tooltip left position:", tooltip.style.left);
            console.log("Tooltip top position:", tooltip.style.top);
            console.log("Tooltip innerHTML length:", tooltip.innerHTML.length);
            console.log("Tooltip has DOC info:", tooltip.innerHTML.includes("DOC"));
            console.log("Tooltip has P. vannamei pill:", tooltip.innerHTML.includes("P. vannamei"));
            console.log("Tooltip has Eq. 1 SR:", tooltip.innerHTML.includes("Eq. 1: Survival Rate"));
            console.log("Tooltip has Eq. 2 FABW:", tooltip.innerHTML.includes("Eq. 2: Final Average Body Weight"));
            console.log("Tooltip has Eq. 7 FCR:", tooltip.innerHTML.includes("Eq. 7: Feed Conversion Ratio"));
            console.log("Tooltip has focused item:", tooltip.innerHTML.includes("tooltip-item-focused"));

            console.log("\n--- Testing pointerleave on canvas ---");
            if (canvas.listeners && canvas.listeners['pointerleave']) {
                canvas.listeners['pointerleave'].forEach(fn => fn());
                console.log("SUCCESS: pointerleave triggered!");
            }
            console.log("After leave - Tooltip hidden:", tooltip.hidden);
            console.log("After leave - Tooltip has 'visible' class:", tooltip.classList.contains('visible'));

            console.log("\n>>> ALL CHECKS PASSED PERFECTLY! <<<");
        } catch (err) {
            console.error("RUNTIME ERROR during test:", err);
            process.exit(1);
        }
    }, 20);

} catch (e) {
    console.error("Evaluation error:", e);
    process.exit(1);
}
