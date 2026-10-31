# -*- coding: utf-8 -*-
"""
Patch static/js/calculators.js tab switching and preset querying for uniform growth section.
"""

def patch_js():
    with open('static/js/calculators.js', 'r', encoding='utf-8') as f:
        content = f.read()

    old_tab_block = '''    // Tab Switching for Growth Calculators
    const growthTabButtons = document.querySelectorAll(".growth-tabs-bar .growth-tab-item");
    const growthTabPanes = document.querySelectorAll(".growth-section .growth-tab-pane");

    growthTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetPaneId = btn.getAttribute("aria-controls");
            growthTabButtons.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            growthTabPanes.forEach(p => {
                p.classList.remove("active");
                p.hidden = true;
            });

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const activePane = document.getElementById(targetPaneId);
            if (activePane) {
                activePane.classList.add("active");
                activePane.hidden = false;
            }
        });
    });'''

    new_tab_block = '''    // Tab Switching for Growth Calculators (Uniform Chip Pills)
    const growthTabButtons = document.querySelectorAll(".tools-tab-chips .preset-chip, .growth-tabs-bar .growth-tab-item");
    const growthTabPanes = document.querySelectorAll(".growth-tab-pane");

    growthTabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const paneKey = btn.dataset.pane || "";
            const targetPaneId = paneKey ? `pane-growth-${paneKey}` : btn.getAttribute("aria-controls");
            growthTabButtons.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            growthTabPanes.forEach(p => {
                p.classList.remove("active");
                p.hidden = true;
                p.style.display = "none";
            });

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const activePane = document.getElementById(targetPaneId);
            if (activePane) {
                activePane.classList.add("active");
                activePane.hidden = false;
                activePane.style.display = "block";
            }
        });
    });'''

    # Normalize newlines
    normalized_old = old_tab_block.replace('\r\n', '\n')
    normalized_content = content.replace('\r\n', '\n')

    if normalized_old not in normalized_content:
        print("Warning: old_tab_block not found verbatim, searching by partial pattern...")
        import re
        pattern = r"// Tab Switching for Growth Calculators[\s\S]+?activePane\.hidden = false;\s*\}\s*\}\);\s*\}\);"
        if re.search(pattern, normalized_content):
            normalized_content = re.sub(pattern, new_tab_block.strip(), normalized_content)
            print("Successfully replaced tab block via regex!")
        else:
            print("Regex pattern also did not match.")
            return False
    else:
        normalized_content = normalized_content.replace(normalized_old, new_tab_block)
        print("Replaced tab block directly.")

    # Also make sure preset buttons query #growth-master-presets .preset-chip
    normalized_content = normalized_content.replace(
        'const growthPresetButtons = document.querySelectorAll(".btn-preset-growth");',
        'const growthPresetButtons = document.querySelectorAll("#growth-master-presets .preset-chip, .btn-preset-growth");'
    )

    with open('static/js/calculators.js', 'w', encoding='utf-8') as f:
        f.write(normalized_content)

    print("Successfully updated static/js/calculators.js!")
    return True

if __name__ == '__main__':
    patch_js()

