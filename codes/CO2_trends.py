# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define relative file paths ---------------------------------------------------
project_dir = Path(__file__).resolve().parent.parent
input_data_dir = project_dir / "data" / "input"
figures_dir = project_dir / "figures"

# Load Data --------------------------------------------------------------------
df_tildas = pd.read_csv(input_data_dir / "goettingen_2023_data_raw.csv")
df_tildas['date_time_measured'] = pd.to_datetime(df_tildas['dateTimeMeasured'], format='%m/%d/%y %H:%M')
df_tildas = df_tildas[df_tildas["SampleName"].str.contains("air", case=False, na=False)]
start = dt.datetime(2023, 7, 11, 12, 0)
end = dt.datetime(2023, 7, 23, 13, 0)
df_tildas = df_tildas[(df_tildas['date_time_measured'] >= start) & (df_tildas['date_time_measured'] <= end)]

df_liang23 = pd.read_csv(input_data_dir / "Liang2023.csv")
df_liang23['Dp17O'] = Dp17O(df_liang23['d17O'], df_liang23['d18O'])

df_hofmann17 = pd.read_csv(input_data_dir / "Hofmann2017_data.csv")
df_hofmann17['Dp17O'] = Dp17O(df_hofmann17['d17O'], df_hofmann17['d18O'])

df_water = pd.read_csv(input_data_dir / "meteoric_water.csv")

df_boering = pd.read_csv(input_data_dir / "Boering2004.csv")
df_boering['Dp17O'] = Dp17O(df_boering['d17O'], df_boering['d18O'])

df_steur = pd.read_csv(input_data_dir / "Steur2024.csv")


# Concatenate all d18O values into one array
all_d18O = np.concatenate([
    df_boering['d18O'],
    df_hofmann17['d18O'],
    df_liang23['d18O'],
    df_steur['d18O_mean']
])

# Calculate mean and standard deviation
mean_all = np.mean(all_d18O)
std_all = np.std(all_d18O, ddof=1)  # use ddof=1 for sample std
print(f"Combined d18O mean: {mean_all:.2f}")
print(f"Combined d18O standard deviation: {std_all:.2f}")

df_horvath12 = pd.read_csv(input_data_dir / "Horvath2012.csv")
df_horvath12 = df_horvath12[df_horvath12.Sample != "human breath"]
horvath_categories = df_horvath12["Sample"].unique()
horvath_colors = dict(zip(horvath_categories, [C["yellow"], C["orange"], C["red6"], C["wgray3"]]))

# Apply plot style -------------------------------------------------------------
apply_plot_style()


# Create figure ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(3.5, 3.5))

# Plot data --------------------------------------------------------------------
# Air CO2
ax.scatter(prime(df_tildas['d18O']), df_tildas['Dp17O'],
            color=C["red"], marker='o', zorder = 10, ec = "k",
            label="Göttingen air CO$_2$ (this study, 07/2023)")

ax.scatter(prime(df_hofmann17['d18O']), df_hofmann17['Dp17O'],
            color="k", marker='.', zorder = -1,
            label="Göttingen air CO$_2$ (Hofmann, 2017)")

ax.scatter(prime(df_liang23[df_liang23['Location'] != "ISL"]['d18O']), df_liang23[df_liang23['Location'] != "ISL"]['Dp17O'],
            color=C["wgray6"], marker=".",
            label="Taiwan air CO$_2$ (Liang, 08/2014 to 11/2017)")

ax.scatter(prime(df_liang23[df_liang23['Location'] == "ISL"]['d18O']), df_liang23[df_liang23['Location'] == "ISL"]['Dp17O'],
            color=C["cgray3"], marker=".",
            label="Israel air CO$_2$ (Liang, 10/2012 to 05/2015)")


ax.scatter(prime(df_steur['d18O_mean']), df_steur['D17O_mean']*1000,
            color=C["blue3"], marker=".",
            label="Lutjewad air CO$_2$ (Steur, 07/2016 to 11/2022)")

# Combustion CO2
for cat in horvath_categories:
    data = df_horvath12[df_horvath12["Sample"] == cat]
    ax.scatter(prime(data['d18O']), data['Dp17O_528'],
               color=horvath_colors[cat], label=f"CO$_2$ from {cat}", ec="k", marker="s")

# Air O2
ax.scatter(prime(23.9), -432,
            color = C["lgreen"], marker='*', s = 70, ec=C["green8"],
            label="air O$_2$")

# Meteoric waters
ax.scatter(prime(df_water['d18O']), Dp17O(df_water['d17O'],df_water['d18O']),
            color=C["green2"], marker='X', ec="k",
            label="meteoric waters")

# Add the leaf CO2/H2O exchange slope
d18o_a = 32
dp17o_a = -190
d18o_b = 48
theta = 0.5229
# The theta slope is defined in prime-transformed isotope coordinates.
dp17o_b = dp17o_a + (theta - 0.528) * (prime(d18o_b) - prime(d18o_a)) * 1000
ax.plot(prime([d18o_a, d18o_b]), [dp17o_a, dp17o_b], color=C["green8"], lw=2, zorder=0)
ax.text(30, -185, "CO$_2$–H$_2$O\nequilibration", ha='right', va='center', color=C["green8"])

# Add annotations
ax.annotate('', xy=(40, 100), xytext=(41, -230+50),
            arrowprops=dict(arrowstyle='fancy', color=C["blue"], lw = 1, shrinkB=9, connectionstyle="arc3,rad=0.00"))
ax.text(39, 0, "stratospheric\nincursion", ha='right', va='center', color=C["blue"])

ax.annotate('', xy=(33, -500), xytext=(41, -230-50),
            arrowprops=dict(arrowstyle='fancy', color=C["orange"], lw = 1, shrinkB=9, connectionstyle="arc3,rad=-0.00"))
ax.text(38, -300, "contribution from\nfossil fuels", ha='right', va='center', color=C["orange"])

# Add legend -------------------------------------------------------------------
add_standard_legend(
    ax, loc="upper left", bbox_to_anchor=(1.02, 1), fontsize=6,
)
# Keep tight_layout from shrinking the axes to accommodate the external legend.
legend = ax.get_legend()
legend.remove()
fig.add_artist(legend)

# Setup axes -------------------------------------------------------------------
setup_axes(fig)
ax.set_xlim(-20, 50)
ax.set_ylim(-555, 105)

# Add axis labels --------------------------------------------------------------
ax.set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm)")
ax.set_xlabel(r"$\delta\prime^{18}\mathrm{O}$ (‰ VSMOW)")

save_figure(fig, figures_dir, "CO2_trends")
