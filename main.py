# %%
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

# %%
# -------------------
# 1. Make hex grid
# -------------------
def hex_vertices(x, y, r=1, orientation="pointy"):
    """Return 6 vertices of a hexagon around (x, y)."""
    start_deg = 30 if orientation == "pointy" else 0
    return [
        (x + r * math.cos(math.radians(start_deg + 60 * i)),
         y + r * math.sin(math.radians(start_deg + 60 * i)))
        for i in range(6)
    ]

rows, cols, r = 10, 10, 1
orientation = "flat"  # just change this line

if orientation == "pointy":
    w = math.sqrt(3) * r
    h = 2 * r
    h_spacing = w
    v_spacing = 3/4 * h
else:
    w = 2 * r
    h = math.sqrt(3) * r
    h_spacing = 3/4 * w
    v_spacing = h

hexes = []
for row in range(rows):
    for col in range(cols):
        if orientation == "pointy":
            cx = col * h_spacing + (row % 2) * (h_spacing / 2)
            cy = row * v_spacing
        else:
            cx = col * h_spacing
            cy = row * v_spacing + (col % 2) * (v_spacing / 2)
        hexes.append({
            "hex_id": row * cols + col,
            "cx": cx,
            "cy": cy,
            "verts": hex_vertices(cx, cy, r, orientation)
        })


combined_df = pd.DataFrame(hexes)
# %%
# -------------------
# 2. Read CSV and clean code
# -------------------
df = pd.read_csv('/Users/aksharkatariya/Documents/GitHub/hex_map_india/state_hex_key.csv')

# keep only letters, take last 2 letters, make uppercase
df["code"] = (
    df.iloc[:, 1]  # assuming 2nd column is the code column
    .astype(str)
    .str.replace("[^A-Za-z]", "", regex=True)
    .str.upper()
    .str[-2:]
)

# keep only needed columns
df = df[["hex_id", "code"]]

# %%
# -------------------
# 3. Merge
# -------------------
merged = combined_df.merge(df, on="hex_id", how="left")
# %%
# -------------------
# 4. Plot
# -------------------
fig, ax = plt.subplots(figsize=(10, 10))
patches = []
colors = []

for _, row in merged.iterrows():
    poly = Polygon(row["verts"], closed=True, edgecolor='black', linewidth=0.5)
    patches.append(poly)
    colors.append("lightgrey" if pd.notna(row["code"]) else "white")

collection = PatchCollection(patches, facecolor=colors, match_original=True)
ax.add_collection(collection)

# label each hex
for _, row in merged.iterrows():
    label = row["code"] if pd.notna(row["code"]) else str(int(row["hex_id"]))
    ax.text(row["cx"], row["cy"], label, ha='center', va='center', fontsize=6)

ax.set_aspect("equal")

# --- Fixes for visibility ---
ax.autoscale()                 # automatically fit all hexes in view
ax.margins(0.1)                # add a little padding
ax.set_axis_off()              # optional: hide borders and ticks
ax.set_title("10x10 Hex Grid with Highlighted States")

plt.show()


# %% plot with only states

# Filter to only hexes that have a code
hexes_with_code = merged[merged["code"].notna()]

# Plot only those hexes
fig, ax = plt.subplots(figsize=(10, 10))
patches = []

for _, row in hexes_with_code.iterrows():
    poly = Polygon(row["verts"], closed=True, edgecolor='black', linewidth=0.5)
    patches.append(poly)

# Create PatchCollection with a single facecolor
collection = PatchCollection(patches, facecolor="lightgrey", match_original=True)
ax.add_collection(collection)

# Label each hex with its code
for _, row in hexes_with_code.iterrows():
    ax.text(row["cx"], row["cy"], row["code"], ha='center', va='center', fontsize=6)

ax.set_aspect("equal")
ax.autoscale()
ax.margins(0.1)
ax.set_axis_off()
ax.set_title("Hex Grid: Only Hexes with Codes")

plt.show()


# %% FUNCTION

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import pandas as pd

def plot_hex_values(df_values, hex_grid=hexes_with_code, code_col="code", value_col="value", cmap_name="viridis"):
    """
    Plots hexagons colored by numeric values.
    
    Parameters:
        df_values : pd.DataFrame
            DataFrame with exactly 2 columns: [code_col, value_col]
        hex_grid : pd.DataFrame
            Hex dataframe with 'code', 'verts', 'cx', 'cy' columns
        code_col : str
            Column name for codes
        value_col : str
            Column name for numeric values
        cmap_name : str
            Matplotlib colormap name
    """
    # Merge input values with hex grid
    plot_df = hex_grid.merge(df_values, on=code_col, how="left")
    
    # Prepare colormap
    vals = plot_df[value_col]
    vmin, vmax = vals.min(), vals.max()
    cmap = cm.get_cmap(cmap_name)
    norm = Normalize(vmin=vmin, vmax=vmax)
    
    # Build patches and colors
    patches, facecolors = [], []
    for _, row in plot_df.iterrows():
        poly = Polygon(row["verts"], closed=True, edgecolor="black", linewidth=0.5)
        patches.append(poly)
        facecolors.append(cmap(norm(row[value_col])))
    
    # Plot
    fig, ax = plt.subplots(figsize=(8, 8))
    collection = PatchCollection(patches, facecolor=facecolors, match_original=True)
    ax.add_collection(collection)
    
    # Labels
    for _, row in plot_df.iterrows():
        ax.text(row["cx"], row["cy"], row[code_col], ha="center", va="center", fontsize=6)
    
    ax.set_aspect("equal")
    ax.autoscale()
    ax.margins(0.05)
    ax.set_axis_off()
    
    # Add colorbar
    from matplotlib.cm import ScalarMappable
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array(vals)
    fig.colorbar(sm, ax=ax, fraction=0.046, pad=0.04, label=value_col)
    
    plt.show()
    
    return plot_df

# %%

literacy = pd.read_csv('/Users/aksharkatariya/Documents/GitHub/hex_map_india/Literacy_data - Sheet1.csv')

plot_hex_values(literacy, value_col="value", code_col="code", cmap_name="plasma")
# %%
