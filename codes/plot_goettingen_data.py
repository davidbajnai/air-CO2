# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

import datetime as dt
from pathlib import Path
from matplotlib.ticker import MultipleLocator
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

# Define relative file paths ---------------------------------------------------
project_dir = Path(__file__).resolve().parent.parent
figures_dir = project_dir / "figures"
output_data_dir = project_dir / "data" / "output"
data_file = output_data_dir / "goettingen_2023_data_scaled.csv"
# Choose "Dp17O_scaled" or "Dp17O_scaled_corrected" from the same export.
dp17o_column = "Dp17O_scaled_corrected"
figure_name = {
    "Dp17O_scaled": "goettingen_2023_data_scaled",
    "Dp17O_scaled_corrected": "goettingen_2023_data_scaled_corrected",
}[dp17o_column]

# Load Data --------------------------------------------------------------------
df_data = pd.read_csv(data_file, parse_dates=["dateTimeMeasured"])
# df_data = df_data[(df_data["pCO2Sam"] - 420).abs() <= 20].copy()
# print(f"Input: {data_file}\nDelta'17O column: {dp17o_column}")

# Apply plot style -------------------------------------------------------------
apply_plot_style()

# Create figure ----------------------------------------------------------------
fig, axes = plt.subplots(3, 1, sharex=True, figsize=(6.5, 6.5))

# Plot data --------------------------------------------------------------------
for ax in axes:
    ax.axvline(dt.datetime(2023, 4, 25, 14), color="k", ls=":", lw=1, zorder=-2)
    ax.axvline(dt.datetime(2023, 6, 9, 11, 30), color="k", ls=":", lw=1, zorder=-2)
    ax.axvline(dt.datetime(2023, 6, 22), color="k", ls=":", lw=1, zorder=-2)

axes[0].scatter(
    df_data["dateTimeMeasured"], df_data["pCO2Sam"],
    fc="black", ec="gray", marker="o",
    zorder=1,
)

axes[1].errorbar(
    df_data["dateTimeMeasured"], df_data["d18O_scaled"],
    yerr=df_data["d18OError"], ls="none", color="black", mec="gray",
    fmt="o", zorder=-1, mew=0.5,
)

axes[2].errorbar(
    df_data["dateTimeMeasured"], df_data[dp17o_column],
    yerr=df_data["Dp17OError"], ls="none", color="black", mec="gray",
    fmt="o", mew=0.5,
)

# Add legend -------------------------------------------------------------------
# No legends are displayed.

# Setup axes -------------------------------------------------------------------
setup_axes(fig)
xmin = df_data["dateTimeMeasured"].min() - dt.timedelta(days=1)
xmax = df_data["dateTimeMeasured"].max() + dt.timedelta(days=1)
axes[-1].set_xlim(xmin, xmax)
axes[2].set_ylim(-326, -174)
axes[2].yaxis.set_major_locator(MultipleLocator(25))

axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=4))
axes[-1].xaxis.set_minor_locator(mdates.DayLocator(interval=1))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

# Add axis labels --------------------------------------------------------------
axes[0].set_ylabel(r"$\chi\prime^{smp}_{626}$ (µmol mol$^{-1}$)")
axes[1].set_ylabel(r"$\delta^{18}\mathrm{O}$ (‰ VSMOW)")
axes[2].set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm)")
axes[-1].set_xlabel("Measurement date")

save_figure(fig, figures_dir, figure_name)
print(f"Figure: {figures_dir / 'png' / (figure_name + '.png')}")

# Print sample statistics ------------------------------------------------------
print(
    f"Delta'17O ({dp17o_column}): {df_data[dp17o_column].mean():.2f} ± "
    f"{df_data[dp17o_column].std():.2f} ppm, "
    f"d18O: {df_data['d18O_scaled'].mean():.2f} ± "
    f"{df_data['d18O_scaled'].std():.2f} ‰ VSMOW "
    f"(mean, 1 SD, n={len(df_data)})"
)
