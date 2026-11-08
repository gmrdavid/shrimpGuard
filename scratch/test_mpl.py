import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
ax.text(0.5, 0.5, "ShrimpGuard Test", ha="center", va="center", fontsize=16)
ax.axis("off")
fig.savefig("scratch/test_mpl.png", bbox_inches="tight")
plt.close(fig)

import os
print("MPL PNG exists:", os.path.exists("scratch/test_mpl.png"))
