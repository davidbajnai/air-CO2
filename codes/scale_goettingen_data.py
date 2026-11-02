# Import libraries -------------------------------------------------------------
from _plot_style import *
from _helper_functions import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import t
import datetime as dt
from pathlib import Path

# Define relative file paths ---------------------------------------------------
figures_dir = Path(__file__).resolve().parent.parent / "figures"
input_data_dir = Path(__file__).resolve().parent.parent / "data" / "input"
output_data_dir = Path(__file__).resolve().parent.parent / "data" / "output"

# Load Data --------------------------------------------------------------------
df_raw = pd.read_csv(input_data_dir / "goettingen_2023_data_raw.csv")

# Apply plot style -------------------------------------------------------------
apply_plot_style()


# Function to print info for scaled samples
def print_info(
    df: pd.DataFrame, d18o_col: str, dp17o_col: str, sample_name: str,
) -> None:
    gas_subset = df[df["SampleName"].str.contains(sample_name)].copy()
    d18o_mean = gas_subset[d18o_col].mean()
    d18o_std = gas_subset[d18o_col].std()
    dp17o_mean = gas_subset[dp17o_col].mean()
    dp17o_std = gas_subset[dp17o_col].std()
    n_gas = len(gas_subset)
    print(f"{sample_name}, N = {n_gas}, d18O = {d18o_mean:.3f}(±{d18o_std:.3f})‰, ∆'17O = {dp17o_mean:.0f}(±{dp17o_std:.0f}) ppm", end="")

# This function scales the data based on the accepted values of the light and heavy reference gases
# The scaling is done for each measurement period separately
def scale_data(
    df: pd.DataFrame, figure_suffix: str = "",
) -> tuple[pd.DataFrame, pd.DataFrame]:

    df["dateTimeMeasured"] = pd.to_datetime(df["dateTimeMeasured"], format="%m/%d/%y %H:%M")

    df["pCO2Mismatch"] = df["pCO2Sam"] - df["pCO2Ref"]

    df = df[df["pCO2Mismatch"].abs() < 2]

    # Filter the data to include only the relevant measurement period
    start = dt.datetime(2023, 6, 22, 0, 0)
    end = dt.datetime(2023, 7, 25, 0, 0)
    df = df[(df['dateTimeMeasured'] >= start) & (df['dateTimeMeasured'] <= end)]

    # Perform the scaling for each measurement period separately
    df_samples = pd.DataFrame()
    reference_mixing_ratios = []
    grouped = df.groupby("measurementPeriod")
    for figure_number, (period, group) in enumerate(grouped):

        print(f"\nMeasurement period {period}:")
        print_info(group, "d18O", "Dp17O", "light")
        print("\t<--- unscaled")
        print_info(group, "d18O", "Dp17O", "heavy")
        print("\t<--- unscaled")

        # Do the scaling here, based on the accepted values of the light and heavy reference gases

        # Measured CO2 values
        heavy_d18o_measured = group[group["SampleName"].str.contains("heavy")]["d18O"].mean()
        heavy_d17o_measured = group[group["SampleName"].str.contains("heavy")]["d17O"].mean()

        light_d18o_measured = group[group["SampleName"].str.contains("light")]["d18O"].mean()
        light_d17o_measured = group[group["SampleName"].str.contains("light")]["d17O"].mean()

        # Accepted CO2 values
        # Linked to NBS-18 and IAEA-603 in Chaillot et al. (2025)
        # heavy_d18O_accepted = 76.475
        # heavy_Dp17O_accepted = -165
        # heavy_d17O_accepted = d17O(heavy_d18O_accepted, heavy_Dp17O_accepted)

        # light_d18O_accepted = -1.139
        # light_Dp17O_accepted = -167
        # light_d17O_accepted = d17O(light_d18O_accepted, light_Dp17O_accepted)

        # Accepted CO2 values
        # Linked to NBS-18 and IAEA-603 in Wostbrock et al. (2020) - see Bajnai et al. (2024) for details
        heavy_d18o_accepted = 76.475
        heavy_dp17o_accepted = -216
        heavy_d17o_accepted = d17O(heavy_d18o_accepted, heavy_dp17o_accepted)

        light_d18o_accepted = -1.139
        light_dp17o_accepted = -143
        light_d17o_accepted = d17O(light_d18o_accepted, light_dp17o_accepted)

        # Calculate the scaling factors
        slope_d18o = (light_d18o_accepted - heavy_d18o_accepted) / (light_d18o_measured - heavy_d18o_measured)
        intercept_d18o = heavy_d18o_accepted - slope_d18o * heavy_d18o_measured

        slope_d17o = (light_d17o_accepted - heavy_d17o_accepted) / (light_d17o_measured - heavy_d17o_measured)
        intercept_d17o = heavy_d17o_accepted - slope_d17o * heavy_d17o_measured

        # Scale the measured values
        group["d18O_scaled"] = slope_d18o*group['d18O']+intercept_d18o
        group["d17O_scaled"] = slope_d17o*group['d17O']+intercept_d17o
        group["Dp17O_scaled"] = Dp17O(group["d17O_scaled"], group["d18O_scaled"])

        # Use the same filtered standards that define the isotope scaling.
        reference_gases = group[group["SampleName"].isin(["lightVsRef", "heavyVsRef"])]
        air_mixing_ratios = group.loc[group["SampleName"] == "air", "pCO2Sam"]
        reference_mixing_ratios.append({
            "measurementPeriod": period,
            "chi_626_light_mean": reference_gases.loc[
                reference_gases["SampleName"] == "lightVsRef", "pCO2Sam"
            ].mean(),
            "chi_626_heavy_mean": reference_gases.loc[
                reference_gases["SampleName"] == "heavyVsRef", "pCO2Sam"
            ].mean(),
            "chi_626_light_std": reference_gases.loc[
                reference_gases["SampleName"] == "lightVsRef", "pCO2Sam"
            ].std(),
            "chi_626_heavy_std": reference_gases.loc[
                reference_gases["SampleName"] == "heavyVsRef", "pCO2Sam"
            ].std(),
            "chi_626_reference_std": reference_gases["pCO2Sam"].std(),
            "air_sample_count": len(air_mixing_ratios),
            "chi_626_air_min": air_mixing_ratios.min(),
            "chi_626_air_max": air_mixing_ratios.max(),
            # Report the pooled mean as a diagnostic, not as the working gas.
            "chi_626_reference": reference_gases["pCO2Sam"].mean(),
        })

        # Assign colors and markers to samples
        categories = group["SampleName"].unique()
        markers = dict(zip(categories, ["o", "s", "D", "v", "^",
                                    "<", ">", "p", "P", "*"]*10))
        colors = {
            "heavyVsRef": C["blue"],
            "lightVsRef": C["orange"],
            "air": C["green"],
        }
        legend_labels = {
            "heavyVsRef": r"heavy CO$_2$",
            "lightVsRef": r"light CO$_2$",
            "air": "air",
        }

        # Create figure --------------------------------------------------------

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(6.5, 6))

        # Plot data ------------------------------------------------------------

        for cat in categories:
            data = group[group["SampleName"] == cat]

            ax1.scatter(data["dateTimeMeasured"], data["pCO2Sam"],
                       marker=markers[cat], fc=colors[cat], label=legend_labels[cat])
            ax1.errorbar(data["dateTimeMeasured"], data["pCO2Sam"],
                         yerr=data["pCO2Sam_error"],
                         fmt="none", color=C["cgray2"], zorder=0)

            ax2.scatter(data["dateTimeMeasured"], data["pCO2Mismatch"],
                        marker=markers[cat], fc=colors[cat])
            ax2.errorbar(data["dateTimeMeasured"], data["pCO2Mismatch"],
                         yerr=data["pCO2Mismatch_error"],
                         fmt="none", color=C["cgray2"], zorder=0)

            ax3.scatter(data["dateTimeMeasured"], data["Dp17O"],
                        marker=markers[cat], fc=colors[cat])
            ax3.errorbar(data["dateTimeMeasured"], data["Dp17O"],
                        yerr=data["Dp17OError"],
                        fmt="none", color=C["cgray2"], zorder=0)

        # Add legend -----------------------------------------------------------
        add_standard_legend(ax1, loc="upper left", bbox_to_anchor=(1.02, 1))

        # Setup axes -----------------------------------------------------------
        setup_axes(fig)
        ax3.xaxis.set_major_locator(mdates.DayLocator(interval=4))
        ax3.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

        # Add axis labels ------------------------------------------------------
        ax1.set_ylabel(r"$\chi\prime^{smp}_{626}$ (µmol mol$^{-1}$)")
        ax2.set_ylabel(r"$\chi\prime^{smp}_{626}$ - $\chi\prime^{ref}_{626}$ (µmol mol$^{-1}$)")
        ax3.set_ylabel(r"$\Delta\prime^{17}\mathrm{O}$ (ppm, unscaled CO$_2$)")
        ax3.set_xlabel("Measurement date")

        period_suffix = f"_{figure_number + 1}" if grouped.ngroups > 1 else ""
        save_figure(
            fig, figures_dir, f"replicates{period_suffix}{figure_suffix}",
        )

        # Exclude the standards from the exported dataframe
        group = group[~group["SampleName"].str.contains("NBS18|IAEA603|light|heavy|DH11|NBS")].copy()
        df_samples = pd.concat([df_samples, group])

    return df_samples, pd.DataFrame(reference_mixing_ratios)


# This function averages the scaled data from multiple measurement periods
def average_data(df: pd.DataFrame) -> pd.DataFrame:
    # Calculate the mean values from the replicate measurements
    df = df.loc[:, ["SampleName", "d18O_scaled", "d17O_scaled", "Dp17O_scaled"]]
    df_mean = df.groupby('SampleName').mean().reset_index()
    df_mean = df_mean.rename(columns={
                         'd18O_scaled': 'd18O_CO2', 'd17O_scaled': 'd17O_CO2', 'Dp17O_scaled': 'Dp17O_CO2'})

    # Calculate reproducibility from replicate measurements
    df_std = df.groupby('SampleName').std().reset_index()
    df_std = df_std.rename(columns={'d18O_scaled': 'd18O_error',
                           'd17O_scaled': 'd17O_error', 'Dp17O_scaled': 'Dp17O_error'})
    df_std['Replicates'] = df.groupby(
        'SampleName').size().reset_index(name='counts')['counts']

    confidence_level = 0.68
    alpha = 1 - confidence_level
    dof = df_std['Replicates'] - 1
    t_crit = t.ppf(1 - alpha / 2, dof)

    for col in ['d18O_error', 'd17O_error', 'Dp17O_error']:
        standard_error = df_std[col] / np.sqrt(df_std['Replicates'])
        df_std[col] = standard_error * t_crit

    df_merged = df_mean.merge(df_std, on='SampleName')
    df = df_merged

    return df


# Data scaling -----------------------------------------------------------------

# Scale the data
df, df_reference_mixing_ratios = scale_data(df_raw)

for reference in df_reference_mixing_ratios.itertuples(index=False):
    print(f"\nMeasurement period {reference.measurementPeriod} mixing ratios:")
    print(
        f"Light CO2 chi_626: {reference.chi_626_light_mean:.0f} "
        f"± {reference.chi_626_light_std:.0f} umol/mol (mean ± 1 SD)"
    )
    print(
        f"Heavy CO2 chi_626: {reference.chi_626_heavy_mean:.0f} "
        f"± {reference.chi_626_heavy_std:.0f} umol/mol (mean ± 1 SD)"
    )
    print(
        f"Pooled reference chi_626: {reference.chi_626_reference:.0f} "
        f"± {reference.chi_626_reference_std:.0f} umol/mol (mean ± 1 SD)"
    )
    print(f"Number of air samples: {reference.air_sample_count}")
    print(
        f"Air sample chi_626 range: {reference.chi_626_air_min:.0f}–"
        f"{reference.chi_626_air_max:.0f} umol/mol (min–max)"
    )

# Mixing ratio correction before scaling ---------------------------------------
# Optional: comment out the code down to "End mixing ratio correction".
# Apply Eq. (9) of Bajnai & Hare (2025) to each replicate, including standards.
mixing_ratio_slope = 5.7  # Delta'17O ppm per umol/mol sample-working gas mismatch.
df_raw_corrected = df_raw.copy()
df_raw_corrected["d17O_uncorrected"] = df_raw_corrected["d17O"]
df_raw_corrected["Dp17O_uncorrected"] = df_raw_corrected["Dp17O"]
df_raw_corrected["chi_626_mismatch"] = (
    df_raw_corrected["pCO2Sam"] - df_raw_corrected["pCO2Ref"]
)
df_raw_corrected["Dp17O_mixing_ratio_correction"] = (
    -mixing_ratio_slope * df_raw_corrected["chi_626_mismatch"]
)
df_raw_corrected["Dp17O"] = (
    df_raw_corrected["Dp17O_uncorrected"]
    + df_raw_corrected["Dp17O_mixing_ratio_correction"]
)
# Scaling acts on d17O, so reconstruct it from the corrected Delta'17O first.
df_raw_corrected["d17O"] = d17O(
    df_raw_corrected["d18O"], df_raw_corrected["Dp17O"],
)

df_corrected, df_reference_mixing_ratios_corrected = scale_data(
    df_raw_corrected, figure_suffix="_corrected",
)
df_corrected = df_corrected.rename(columns={
    "d17O_scaled": "d17O_scaled_corrected",
    "Dp17O_scaled": "Dp17O_scaled_corrected",
})
# Add corrected isotope columns without replacing the original scaled values.
df = df.merge(
    df_corrected[["ID", "d17O_scaled_corrected", "Dp17O_scaled_corrected"]],
    on="ID",
)
# End mixing ratio correction --------------------------------------------------

# Export data ------------------------------------------------------------------
export_table(df, "goettingen_2023_data_scaled", output_data_dir)

print(
    f"Corrected scaled d18O: min = {df_corrected['d18O_scaled'].min():.1f}, "
    f"max = {df_corrected['d18O_scaled'].max():.1f} ‰"
)
print(
    f"Corrected scaled ∆17O: min = {df_corrected['Dp17O_scaled_corrected'].min():.0f}, "
    f"max = {df_corrected['Dp17O_scaled_corrected'].max():.0f} ppm"
)
