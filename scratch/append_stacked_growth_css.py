# -*- coding: utf-8 -*-
"""
Update static/css/style.css to include the stacked grid styles for Section 2.
"""

stacked_css = '''
/* Growth Stacked Layout: Parameters on top, 8 Metrics Grid below */
.calculators-page .growth-parameters-wrapper {
    margin-bottom: 24px;
}

.calculators-page .growth-form-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
}

@media (max-width: 1200px) {
    .calculators-page .growth-form-grid {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }
}

@media (max-width: 850px) {
    .calculators-page .growth-form-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 550px) {
    .calculators-page .growth-form-grid {
        grid-template-columns: 1fr;
    }
}

.calculators-page .growth-metrics-wrapper {
    margin-top: 26px;
    padding-top: 22px;
    border-top: 1px solid #eef2f6;
}

.calculators-page .growth-metrics-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}

.calculators-page .growth-metrics-header .tools-subheading {
    margin: 0 0 3px 0;
}

.calculators-page .growth-metrics-sub {
    font-size: 12.5px;
    color: #64748b;
}

.calculators-page .growth-metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
}

@media (max-width: 1200px) {
    .calculators-page .growth-metrics-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 650px) {
    .calculators-page .growth-metrics-grid {
        grid-template-columns: 1fr;
    }
}
'''

def update_css():
    with open('static/css/style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '/* Growth Stacked Layout: Parameters on top, 8 Metrics Grid below */'
    if marker in content:
        print("Stacked layout CSS already present.")
        return

    # Append before EOF or at growth section
    insert_point = '/* Modal Popup Dialog Styles */'
    if insert_point in content:
        content = content.replace(insert_point, stacked_css.strip() + '\n\n' + insert_point)
    else:
        content += '\n\n' + stacked_css.strip()

    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated static/css/style.css with stacked growth layout styles!")

if __name__ == '__main__':
    update_css()

