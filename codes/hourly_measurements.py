# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

import datetime as dt
from pathlib import Path

from astral import LocationInfo
from astral.sun import sun
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from meteostat import config, hourly, Station
import pandas as pd
from scipy.stats import linregress

# Define relative file paths ---------------------------------------------------
project_dir = Path(__file__).resolve().parent.parent
figures_dir = project_dir / "figures"
input_data_dir = project_dir / "data" / "input"
output_data_dir = project_dir / "data" / "output"
data_file = output_data_dir / "goettingen_2023_data_scaled.csv"
dp17o_column = "Dp17O_scaled_corrected"
figure_name = f"hourly_measurements_{dp17o_column}"

# Load Data --------------------------------------------------------------------
start = dt.datetime(2023, 7, 11, 12)
end = dt.datetime(2023, 7, 23, 13)
local_timezone = "Europe/Berlin"

df = pd.read_csv(data_file, parse_dates=["dateTimeMeasured"])
df = df.loc[
    df["SampleName"].eq("air") & df["dateTimeMeasured"].between(start, end)
].sort_values("dateTimeMeasured").copy()

# The model interpolation must include only numeric columns.
df_model = pd.read_csv(input_data_dir / "Hofmann2017_model.csv")
df_model["Date"] = pd.to_datetime(df_model["Date_2023"])
df_model = (
    df_model.set_index("Date")[["Dp17O"]]
    .resample("D").asfreq().interpolate().reset_index()
)

# Query and plot weather in the same local time as the measurement timestamps.
config.cache_directory = str(project_dir / "data" / "cache" / "meteostat")
weather = hourly(Station(id="10444"), start, end, timezone=local_timezone).fetch()
weather = weather.rename_axis("time").reset_index().sort_values("time")
weather["time"] = weather["time"].dt.tz_localize(None)

city = LocationInfo("Göttingen", "Germany", local_timezone, 51.5406, 9.9366)
dates = pd.date_range(start.date(), end.date(), freq="D")
sunrises = []
sunsets = []
for date in dates:
    sunlight = sun(city.observer, date=date.date(), tzinfo=local_timezone)
    # Matplotlib treats naive datetimes as UTC; keep all plotted times local-naive.
    sunrises.append(sunlight["sunrise"].replace(tzinfo=None))
    sunsets.append(sunlight["sunset"].replace(tzinfo=None))

# Interpolate hourly temperatures to the exact measurement times.
temperature = weather.set_index("time")["temp"]
measurement_times = pd.DatetimeIndex(df["dateTimeMeasured"])
df["temperature_interpolated"] = (
    temperature.reindex(temperature.index.union(measurement_times))
    .interpolate(method="time", limit_area="inside")
    .reindex(measurement_times).to_numpy()
)
measurement_columns = ["pCO2Sam", "d18O_scaled", dp17o_column]
for column in measurement_columns:
    paired = df[["temperature_interpolated", column]].dropna()
    regression = linregress(paired["temperature_interpolated"], paired[column])
    print(f"{column}: r2 = {regression.rvalue**2:.2f}, p_value = {regression.pvalue:.3f}")

# Apply plot style -------------------------------------------------------------
apply_plot_style()

# Create figure ----------------------------------------------------------------
fig, panel_axes = plt.subplots(
    3, 2, sharex="col", sharey="row", figsize=(6.5, 5.2),
    gridspec_kw={"width_ratios": [3, 1]},
)
axes = panel_axes[:, 0]
crossplot_axes = panel_axes[:, 1]
# Keep the original wide time-series proportions beside square crossplots.
for ax, crossplot_ax in zip(axes, crossplot_axes):
    ax.set_box_aspect(1 / 3)
    crossplot_ax.set_box_aspect(1)
# Create one temperature axis per panel, rather than one per day.
temperature_axes = [ax.twinx() for ax in axes]

# Plot data --------------------------------------------------------------------
twilight_duration = dt.timedelta(minutes=60)
for ax, temperature_ax in zip(axes, temperature_axes):
    for date, sunrise, sunset in zip(dates, sunrises, sunsets):
        day_start = date.to_pydatetime()
        day_end = day_start + dt.timedelta(days=1)
        dawn_start = sunrise - twilight_duration
        dusk_end = sunset + twilight_duration
        ax.axvspan(day_start, dawn_start, color=C["blue8"], alpha=0.31, ec="none")
        ax.axvspan(dusk_end, day_end, color=C["blue8"], alpha=0.31, ec="none")
        ax.axvspan(dawn_start, sunrise, color=C["blue8"], alpha=0.19, ec="none")
        ax.axvspan(sunset, dusk_end, color=C["blue8"], alpha=0.19, ec="none")
    temperature_ax.plot(weather["time"], weather["temp"], color=C["red4"], alpha=0.6, lw=1.1)

for sunrise, sunset in zip(sunrises, sunsets):
    midday = sunrise + (sunset - sunrise) / 2
    if start <= sunrise and sunset <= end:
        axes[0].text(
            midday, 1.04, "\u2600", color=C["orange"], fontsize=14,
            ha="center", va="bottom", transform=axes[0].get_xaxis_transform(),
        )
for sunset, next_sunrise in zip(sunsets[:-1], sunrises[1:]):
    dusk_end = sunset + twilight_duration
    night_midpoint = dusk_end + (next_sunrise - dusk_end) / 2
    if start <= dusk_end and next_sunrise <= end:
        axes[0].text(
            night_midpoint, 1.04, "\u263E", color=C["blue8"], alpha=0.5,
            fontsize=14, ha="center", va="bottom",
            transform=axes[0].get_xaxis_transform(),
        )

axes[0].plot(
    df["dateTimeMeasured"], df["pCO2Sam"],
    color=C["cgray8"], marker="o", ms=5, ls="-", lw=1,
)
axes[1].errorbar(
    df["dateTimeMeasured"], df["d18O_scaled"], yerr=df["d18OError"],
    color=C["cgray8"], marker="o", ms=5, ls="-", lw=1,
)
axes[2].errorbar(
    df["dateTimeMeasured"], df[dp17o_column], yerr=df["Dp17OError"],
    color=C["cgray8"], marker="o", ms=5, ls="-", lw=1,
)
axes[2].plot(
    df_model["Date"], df_model["Dp17O"], color=C["lgreen"],
    marker="none", ls="--", lw=2, zorder=1,
    label=r"Hofmann $\it{et}$ $\it{al.}$ (2017) model",
)
for crossplot_ax, column in zip(crossplot_axes, measurement_columns):
    crossplot_ax.scatter(
        df["temperature_interpolated"], df[column], color=C["cgray8"], s=25,
    )

# Add legend -------------------------------------------------------------------
axes[2].legend(fontsize=6, loc="lower left")

# Setup axes -------------------------------------------------------------------
setup_axes(fig)
for ax, temperature_ax in zip(axes, temperature_axes):
    # Temperature overlay axes should not carry additional panel letters.
    temperature_ax.texts[-1].remove()
    temperature_ax.set_zorder(ax.get_zorder() - 1)
    ax.patch.set_visible(False)
    temperature_ax.tick_params(axis="y", colors=C["red4"])
axes[-1].set_xlim(start - dt.timedelta(hours=2), end + dt.timedelta(hours=1))
axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=2))
axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
axes[-1].xaxis.set_minor_locator(mdates.HourLocator(byhour=12))

# Add axis labels --------------------------------------------------------------
axes[0].set_ylabel(r"$\chi\prime^{smp}_{626}$ (µmol mol$^{-1}$)")
axes[1].set_ylabel(r"$\delta^{18}\mathrm{O}$ (‰ VSMOW)")
axes[2].set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm)")
axes[-1].set_xlabel("Measurement time")
for ax, crossplot_ax in zip(axes, crossplot_axes):
    crossplot_ax.set_xlabel("Temperature (°C)")
    crossplot_ax.set_ylabel(ax.get_ylabel())
for temperature_ax in temperature_axes:
    temperature_ax.set_ylabel("Temperature (°C)", color=C["red4"])

save_figure(fig, figures_dir, figure_name)
print(f"Figure: {figures_dir / 'png' / (figure_name + '.png')}")
