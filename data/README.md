# Data

For each instrument we tested, we acquired spectra of acetonitrile (a standard) and several different strains of unicellular algae within the genus, *Chlamydomonas*. 
The sample preparation for the  strains is described in the notebook pub.
The data is organized into directories for each instrument, expanded below.

### Organization

```
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
─ Wasatch_WP785X
  ├── CC-124_TAP_WP-02071.csv
  ├── acetonitrile.csv
  └── chlamy_spectra.tar
```

### Working with the data

The data is there for the taking, so have at it. The module, [`load_spectra.py`](../src/analysis/load_spectra.py), was created to facilitate loading each group of spectral data. This module provides three separate functions:
- `load_acetonitrile_spectra()` -> returns the set of acetonitrile spectra measured by each instrument.
- `load_cc124_tap_spectra()` -> returns the set of spectra for one particular strain of algal cells grown in one particular media (strain CC-124, grown in TAP) measured by each instrument.
- `load_chlamy_spectra()` -> returns the full set of spectra of all three algal strains grown in two different types of media measured by each instrument, and a corresponding pandas DataFrame.

See the notebook pub for example usage of these functions.


<!-- 
*Maybe delete the intensity parameter? Not clear (e.g. for Wasatch) whether intensity is a fraction of the total power or the selected power. fraction of total power makes sense intuitively to me, but the math doesn't math...*

Other questions:
* do we know if any of these have built in preprocessing? I saw the Renishaw does automated cosmic ray removal, but what about the others? -->

## Acquisition settings for each instrument

### Horiba MacroRAM
*Brief description*

| -            | Acetonitrile | Chlamydomonas cells |
|--------------|--------------|---------------------|
| Wavelength   | 785 nm       | -                   |
| Power        | 60 mW        | 50 mW               |
| Intensity    | -            | -                   |
| Exposure     | 10 s         | 10 s                |
| Num averages | 5            | 5                   |
| Grating      | 685 1/mm     | -                   |


### OpenRAMAN
*Brief description*

| -            | Acetonitrile | Chlamydomonas cells |
|--------------|--------------|---------------------|
| Wavelength   | 532 nm       | -                   |
| Power        | 4 mW         | -                   |
| Intensity    | -            | -                   |
| Exposure     | 10 s         | 5 s                 |
| Num averages | 5            | 2                   |
| Grating      | ?            | -                   |


### Renishaw Qontor
*Brief description*

| -            | Acetonitrile | Chlamydomonas cells |
|--------------|--------------|---------------------|
| Wavelength   | 785 nm       | -                   |
| Power        | 300 mW       | -                   |
| Intensity    | 10%          | -                   |
| Exposure     | 10 s         | -                   |
| Num averages | 5            | -                   |
| Grating      | ?            | -                   |

**Notes**:
- Preprocessing: cosmic ray removal
- Cells prepped on glass slides -- big hump around 1400 cm^-1


### Wasatch WP 785X
*Brief description*

| -            | Acetonitrile | Chlamydomonas cells |
|--------------|--------------|---------------------|
| Wavelength   | 785 nm       | -                   |
| Power        | 100 mW       | 50 mW               |
| Intensity    | 35.9%        | 26.7%               |
| Exposure     | 1 s          | 3 s                 |
| Num averages | 2            | -                   |
| Grating      | ?            | -                   |
