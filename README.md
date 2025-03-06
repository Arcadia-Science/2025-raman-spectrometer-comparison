# Comparison of spontaneous Raman spectrometers

[![Arcadia Pub](https://img.shields.io/badge/Arcadia-Pub-596F74.svg?logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDI3LjcuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPgo8c3ZnIHZlcnNpb249IjEuMSIgaWQ9IkxheWVyXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4IgoJIHZpZXdCb3g9IjAgMCA0My4yIDQwLjQiIHN0eWxlPSJlbmFibGUtYmFja2dyb3VuZDpuZXcgMCAwIDQzLjIgNDAuNDsiIHhtbDpzcGFjZT0icHJlc2VydmUiPgo8c3R5bGUgdHlwZT0idGV4dC9jc3MiPgoJLnN0MHtmaWxsOm5vbmU7c3Ryb2tlOiNGRkZGRkY7c3Ryb2tlLXdpZHRoOjI7c3Ryb2tlLWxpbmVqb2luOmJldmVsO3N0cm9rZS1taXRlcmxpbWl0OjEwO30KPC9zdHlsZT4KPGc+Cgk8cG9seWdvbiBjbGFzcz0ic3QwIiBwb2ludHM9IjIxLjYsMyAxLjcsMzcuNCA0MS41LDM3LjQgCSIvPgoJPGxpbmUgY2xhc3M9InN0MCIgeDE9IjIxLjYiIHkxPSIzIiB4Mj0iMjEuNiIgeTI9IjI3LjMiLz4KCTxwb2x5bGluZSBjbGFzcz0ic3QwIiBwb2ludHM9IjEyLjIsMTkuNCAyNC42LDMwLjEgMjQuNiwzNy40IAkiLz4KCTxsaW5lIGNsYXNzPSJzdDAiIHgxPSIxNy42IiB5MT0iMTYuNyIgeDI9IjE3LjYiIHkyPSIyNC4xIi8+Cgk8bGluZSBjbGFzcz0ic3QwIiB4MT0iMjguNiIgeTE9IjE1LjIiIHgyPSIyMS43IiB5Mj0iMjIuMSIvPgoJPHBvbHlsaW5lIGNsYXNzPSJzdDAiIHBvaW50cz0iNi44LDI4LjcgMTkuNSwzNC40IDE5LjUsMzcuNCAJIi8+Cgk8bGluZSBjbGFzcz0ic3QwIiB4MT0iMzQuOCIgeTE9IjI1LjgiIHgyPSIyNC42IiB5Mj0iMzYuMSIvPgoJPGxpbmUgY2xhc3M9InN0MCIgeDE9IjI5LjciIHkxPSIyMi4yIiB4Mj0iMjkuNyIgeTI9IjMwLjkiLz4KPC9nPgo8L3N2Zz4K)](https://doi.org/10.57844/arcadia-fe2a-711e)

<img src=assets/acetonitrile_figure.png alt=tracked cells width=720>

## Purpose

This code repository contains all materials required for creating and hosting the publication entitled, ["Comparison of spontaneous Raman spectrometers"](https://arcadia-science.github.io/2025-raman-spectrometer-comparison/).

## Data Description

For each Raman spectroscopy instrument we tested, we acquired spectra of acetonitrile (a standard) and several different strains of unicellular algae within the genus, *Chlamydomonas*. 
The sample preparation for the cell cultures is described in the notebook pub, as is a table of acquisition settings and descriptions of each spectrometer.
The data is organized into directories for each instrument, expanded below.

### Organization
```
$ tree -L 2 data/

─ Horiba_MacroRAM
  ├── CC-124-TAP-2.txt
  ├── acetonitrile.txt
  └── chlamy_spectra.tar
─ OpenRAMAN
  ├── CC-124_TAP_Pos-2-000_002.csv
  ├── acetonitrile_n_n_n_solid_10000_0_5.csv
  ├── chlamy_spectra.tar
  └── neon_n_n_n_solid_10000_0_5.csv
─ Renishaw_Qontor
  ├── CC-124_TAP_plate_5x_3_points.txt
  ├── acetonitrile_5x.txt
  ├── chlamy_spectra.tar
  └── glass_slide_background.txt
─ Wasatch_WP532X
  ├── CC-124_TAP_Pos-4-002_001.csv
  ├── acetonitrile.csv
  └── chlamy_spectra.tar
─ Wasatch_WP785X
  ├── CC-124_TAP_WP-02071.csv
  ├── acetonitrile.csv
  └── chlamy_spectra.tar
```

### Working with the data

The module, [`load_spectra.py`](../src/analysis/load_spectra.py), was created to facilitate loading each group of spectral data. This module provides three separate functions:
- `load_acetonitrile_spectra()` -> returns the set of acetonitrile spectra measured by each instrument, and a corresponding pandas DataFrame.
- `load_cc124_tap_spectra()` -> returns the set of spectra for one particular strain of algal cells grown in one particular media (strain CC-124, grown in TAP) measured by each instrument, and a corresponding pandas DataFrame.
- `load_chlamy_spectra()` -> returns the full set of spectra of all three algal strains grown in two different types of media measured by each instrument, and a corresponding pandas DataFrame.

See the notebook pub for example usage of these functions.

## Reproduce

Please see [SETUP.qmd](SETUP.qmd).

## Contribute

Please see [CONTRIBUTING.qmd](CONTRIBUTING.qmd).
