# Supplementary material for:</br>Primary Productivity resolved by interhemispheric measurements of triple oxygen isotopes in atmospheric CO<sub>2</sub>

## Graphical abstract

![Graphical abstract](figures/png/hourly_measurements_Dp17O_scaled_corrected.png)

## Reference

Ghoshmaulik et al. Primary Productivity resolved by interhemispheric measurements of triple oxygen isotopes in atmospheric CO<sub>2</sub>. Under review.

## Codes

- [scale_goettingen_data.py](codes/scale_goettingen_data.py) scales the Göttingen CO<sub>2</sub> triple oxygen isotope measurements using reference gases and provides results with and without a correction for sample–reference mixing-ratio differences. Input: [goettingen_2023_data_raw.csv](data/input/goettingen_2023_data_raw.csv). Outputs: scaled measurements in [goettingen_2023_data_scaled.csv](data/output/goettingen_2023_data_scaled.csv) and [goettingen_2023_data_scaled.xlsx](data/output/goettingen_2023_data_scaled.xlsx); replicate diagnostics showing sample mixing ratios, sample–reference mixing-ratio differences, and unscaled Δ’17O through time before correction ([PNG](figures/png/replicates.png), [SVG](figures/svg/replicates.svg)) and after correction ([PNG](figures/png/replicates_corrected.png), [SVG](figures/svg/replicates_corrected.svg)).

- [plot_goettingen_data.py](codes/plot_goettingen_data.py) plots the Göttingen measurements through time. Input: [goettingen_2023_data_scaled.csv](data/output/goettingen_2023_data_scaled.csv). Outputs: [goettingen_2023_data_scaled_corrected.png](figures/png/goettingen_2023_data_scaled_corrected.png) and [goettingen_2023_data_scaled_corrected.svg](figures/svg/goettingen_2023_data_scaled_corrected.svg).

- [hourly_measurements.py](codes/hourly_measurements.py) compares the July 2023 Göttingen air measurements with temperature and a seasonal isotope model. Inputs: [goettingen_2023_data_scaled.csv](data/output/goettingen_2023_data_scaled.csv), [Hofmann2017_model.csv](data/input/Hofmann2017_model.csv), and hourly weather data retrieved from Meteostat. Outputs: [hourly_measurements_Dp17O_scaled_corrected.png](figures/png/hourly_measurements_Dp17O_scaled_corrected.png) and [hourly_measurements_Dp17O_scaled_corrected.svg](figures/svg/hourly_measurements_Dp17O_scaled_corrected.svg).

- [CO2_trends.py](codes/CO2_trends.py) compares the Göttingen air measurements with published CO<sub>2</sub> and meteoric-water isotope data. Inputs: [goettingen_2023_data_raw.csv](data/input/goettingen_2023_data_raw.csv), [Liang2023.csv](data/input/Liang2023.csv), [Hofmann2017_data.csv](data/input/Hofmann2017_data.csv), [Boering2004.csv](data/input/Boering2004.csv), [Steur2024.csv](data/input/Steur2024.csv), [Horvath2012.csv](data/input/Horvath2012.csv), and [meteoric_water.csv](data/input/meteoric_water.csv). Outputs: [CO2_trends.png](figures/png/CO2_trends.png) and [CO2_trends.svg](figures/svg/CO2_trends.svg).

- [_helper_functions.py](codes/_helper_functions.py) provides shared isotope calculations and table export functions.

- [_plot_style.py](codes/_plot_style.py) provides the shared figure styling, colors, legends, and figure export functions.

## Data files

### Input data files

- [goettingen_2023_data_raw.csv](data/input/goettingen_2023_data_raw.csv) contains the raw Göttingen air and reference-gas replicate measurements and the corresponding analytical parameters. It is used by [scale_goettingen_data.py](codes/scale_goettingen_data.py) and [CO2_trends.py](codes/CO2_trends.py).

### Literature data

- [Hofmann2017_data.csv](data/input/Hofmann2017_data.csv) contains dated Göttingen atmospheric CO<sub>2</sub> mixing ratios and carbon and oxygen isotope measurements. It is used by [CO2_trends.py](codes/CO2_trends.py).

- [Hofmann2017_model.csv](data/input/Hofmann2017_model.csv) contains seasonal model Δ’17O values with decimal months and corresponding dates for 2010 and 2023. It is used by [hourly_measurements.py](codes/hourly_measurements.py).

- [Liang2023.csv](data/input/Liang2023.csv) contains atmospheric CO<sub>2</sub> mixing ratios and carbon and oxygen isotope measurements with sampling locations and dates. It is used by [CO2_trends.py](codes/CO2_trends.py).

- [Boering2004.csv](data/input/Boering2004.csv) contains atmospheric CO<sub>2</sub> oxygen isotope measurements with altitude, latitude, temperature, and N2O data. It is used by [CO2_trends.py](codes/CO2_trends.py).

- [Steur2024.csv](data/input/Steur2024.csv) contains dated Lutjewad atmospheric CO<sub>2</sub> mixing ratios and carbon and oxygen isotope measurements with associated uncertainties. It is used by [CO2_trends.py](codes/CO2_trends.py).

- [Horvath2012.csv](data/input/Horvath2012.csv) contains carbon and oxygen isotope measurements of CO<sub>2</sub> from different sources, including combustion, and Δ’17O values calculated with two reference slopes. It is used by [CO2_trends.py](codes/CO2_trends.py).

- [meteoric_water.csv](data/input/meteoric_water.csv) contains meteoric-water δ17O and δ18O measurements, sample identifiers, and source references. It is used by [CO2_trends.py](codes/CO2_trends.py).

### Exported data files

- [goettingen_2023_data_scaled.csv](data/output/goettingen_2023_data_scaled.csv) contains the scaled Göttingen sample measurements, including isotope values with and without the mixing-ratio correction and the corresponding analytical parameters. It is generated by [scale_goettingen_data.py](codes/scale_goettingen_data.py) and used by [plot_goettingen_data.py](codes/plot_goettingen_data.py) and [hourly_measurements.py](codes/hourly_measurements.py).

## License

All files in this repository are available under CC0 1.0. No rights reserved.
