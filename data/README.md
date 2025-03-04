# Data

For each instrument we tested, we acquired spectra of acetonitrile (a standard) and several different strains of unicellular algae within the genus, *Chlamydomonas*. 
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
