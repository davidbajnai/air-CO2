import numpy as np
import pandas as pd


def VSMOW_to_VPDB(VSMOW):
    return 0.97001*VSMOW-29.99


def VPDB_to_VSMOW(VPDB):
    return 1.03092*VPDB+30.92


def prime(x):
    """Convert delta notation to prime notation.

    Parameters
    ----------
    x : array-like or float
        Isotopic composition in per mil.

    Returns
    -------
    numpy.ndarray or float
        Prime-transformed isotope values in per mil.
    """
    x_arr = np.asarray(x, dtype=float)
    return 1000.0 * np.log1p(x_arr / 1000.0)


def unprime(x):
    """Convert prime notation back to delta notation.

    Parameters
    ----------
    x : array-like or float
        Prime-transformed isotope values in per mil.

    Returns
    -------
    numpy.ndarray or float
        Isotopic composition in per mil.
    """
    x_arr = np.asarray(x, dtype=float)
    return np.expm1(x_arr / 1000.0) * 1000.0


def Dp17O(d17O, d18O):
    """Calculate ∆'17O from d17O and d18O values.

    Parameters
    ----------
    d17O : array-like or float
        d17O values in per mil.
    d18O : array-like or float
        d18O values in per mil.

    Returns
    -------
    numpy.ndarray or float
        ∆'17O values in ppm.
    """
    d17_prime = prime(d17O)
    d18_prime = prime(d18O)
    return (d17_prime - 0.528 * d18_prime) * 1000.0


def d17O(d18O, Dp17O):
    """Reconstruct d17O from d18O and ∆'17O.

    Parameters
    ----------
    d18O : array-like or float
        d18O values in per mil.
    Dp17O : array-like or float
        ∆'17O values in ppm.

    Returns
    -------
    numpy.ndarray or float
        d17O values in per mil.
    """
    d18_prime = prime(d18O)
    return unprime(np.asarray(Dp17O, dtype=float) / 1000.0 + 0.528 * d18_prime)


def mix_d17O(
    d18O_A: float,
    d18O_B: float,
    d17O_A: float | None = None,
    Dp17O_A: float | None = None,
    d17O_B: float | None = None,
    Dp17O_B: float | None = None,
    step: int = 100,
):
    """Generate binary mixing trajectories in triple oxygen isotope space.

    This function linearly mixes endmembers A and B in isotope ratio space and
    returns d17O, d18O, and ∆'17O along the mixing path.

    Parameters
    ----------
    d18O_A, d18O_B : float
        Endmember d18O values in per mil.
    d17O_A, d17O_B : float, optional
        Endmember d17O values in per mil.
    Dp17O_A, Dp17O_B : float, optional
        Endmember ∆'17O values in ppm. Used only when d17O_* is not
        supplied.
    step : int, default 100
        Number of equal intervals for mixing between 0 and 100% B.

    Returns
    -------
    pandas.DataFrame
        Columns: mix_d17O, mix_d18O, mix_Dp17O, xB.
    """
    if step <= 0:
        raise ValueError("step must be a positive integer.")

    ratio_B = np.linspace(0.0, 1.0, int(step) + 1, dtype=float)
    ratio_A = 1.0 - ratio_B

    d18O_A = float(d18O_A)
    d18O_B = float(d18O_B)

    if d17O_A is None:
        if Dp17O_A is None:
            raise ValueError("Provide either d17O_A or Dp17O_A.")
        d17O_A = unprime(float(Dp17O_A) / 1000.0 + 0.528 * prime(d18O_A))

    if d17O_B is None:
        if Dp17O_B is None:
            raise ValueError("Provide either d17O_B or Dp17O_B.")
        d17O_B = unprime(float(Dp17O_B) / 1000.0 + 0.528 * prime(d18O_B))

    d17O_A = float(d17O_A)
    d17O_B = float(d17O_B)

    mix_d18O = ratio_B * d18O_B + ratio_A * d18O_A
    mix_d17O = ratio_B * d17O_B + ratio_A * d17O_A
    mix_Dp17O = Dp17O(mix_d17O, mix_d18O)
    xB = ratio_B * 100.0

    df = pd.DataFrame(
        {"mix_d17O": mix_d17O, "mix_d18O": mix_d18O, "mix_Dp17O": mix_Dp17O, "xB": xB}
    )
    return df



def applyAFF(d18O_CO2, d17O_CO2, mineral, temperature_C):

    mineral = mineral.lower()

    # Acid fractionation factors at 90 C
    if mineral == "calcite":
        a18_90 = 1.008146
        a18_25 = 1.01025
        a18_70 = 1.008709

    elif mineral == "aragonite":
        a18_25 = 1.010596
        a18_90 = 1.008541
        a18_70 = 1.00909
    
    elif mineral == "dolomite":
        # Rosenbaum and Sheppard (1986)
        a18_90 = np.exp((6.65*10**5*(1/(90+273.15)**2)+4.23)/1000)
        a18_25 = np.mean([1.01178, 1.01186])
    else:
        raise ValueError(f"Unsupported mineral: {mineral}")

    if temperature_C == 90:
        a18 = a18_90
        theta_acid = 1.2019/(90+273.15) + 0.5192
    elif temperature_C == 25:
        a18 = a18_25
        theta_acid = 1.2019/(25+273.15) + 0.5192
    elif temperature_C == 70:
        a18 = a18_70
        theta_acid = 1.2019/(70+273.15) + 0.5192

    else:
        raise ValueError("temperature_C must be 25, 70, or 90.")

    d18O_AC = (d18O_CO2 + 1000) / a18 - 1000
    d17O_AC = (d17O_CO2 + 1000) / (a18 ** theta_acid) - 1000
    Dp17O_AC = Dp17O(d17O_AC, d18O_AC)

    return d18O_AC, d17O_AC, Dp17O_AC



def export_table(df, file_name, data_dir, print_columns=None, include_index=False):
    """Export a table DataFrame as both CSV and XLSX, and optionally print columns.
    """
    from pathlib import Path
    from openpyxl import load_workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill
    from tabulate import tabulate

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    csv_path = data_path / f"{file_name}.csv"
    xlsx_path = data_path / f"{file_name}.xlsx"

    df.to_csv(csv_path, index=include_index)
    df.to_excel(xlsx_path, index=include_index)

    # Apply workbook styling after export.
    wb = load_workbook(xlsx_path)
    ws = wb.active

    header_fill = PatternFill(fill_type="solid", fgColor="B4D5F6")
    header_font = Font(bold=True)
    no_border = Border()
    left_align = Alignment(horizontal="left")
    column_index_by_name = {}
    for col_idx in range(1, ws.max_column + 1):
        header_value = ws.cell(row=1, column=col_idx).value
        if header_value is not None:
            column_index_by_name[str(header_value)] = col_idx

    # Style cells in the used range and format the header row.
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.border = no_border
            cell.alignment = left_align
            if cell.row == 1:
                cell.font = header_font
                cell.fill = header_fill

    # Format numeric data columns; keep Replicates as integer.
    for col_name in df.columns:
        col_idx = column_index_by_name.get(str(col_name))
        if col_idx is None:
            continue
        if col_name == "Replicates":
            number_format = "0"
        elif pd.api.types.is_numeric_dtype(df[col_name]):
            number_format = "0.00"
        else:
            continue

        for row_idx in range(2, ws.max_row + 1):
            ws.cell(row=row_idx, column=col_idx).number_format = number_format

    # Approximate auto-fit width from rendered cell text length.
    for col_cells in ws.iter_cols(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        max_len = 0
        for cell in col_cells:
            value_len = len(str(cell.value)) if cell.value is not None else 0
            if value_len > max_len:
                max_len = value_len

        ws.column_dimensions[col_cells[0].column_letter].width = max_len + 2

    wb.save(xlsx_path)

    if print_columns is True:
        printable_df = df
    elif isinstance(print_columns, list):
        missing_cols = [col for col in print_columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Columns not found in DataFrame: {missing_cols}")
        printable_df = df[print_columns]
    elif print_columns in (None, False):
        printable_df = None
    else:
        raise TypeError("print_columns must be a list of column names, True, False, or None")

    if printable_df is not None:
        print(tabulate(printable_df, headers="keys", tablefmt="simple_outline", showindex=False))
        print(f"Number of rows: {len(printable_df)}")

    return str(csv_path), str(xlsx_path)