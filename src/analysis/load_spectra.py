import os
import re
import shutil
import tarfile
import tempfile
from fnmatch import fnmatch
from pathlib import Path

import pandas as pd
from ramanalysis import RamanSpectrum
from ramanalysis.readers import read_renishaw_multipoint_txt

REPO_ROOT_DIRECTORY = Path(__file__).parents[2]
DATA_DIRECTORY = REPO_ROOT_DIRECTORY / "data"


def tar_wrapper_single(
    tarpath: str | Path,
    filename: str,
    function: callable,
    **kwargs,
):
    """Wrapper for extracting a single file object from a tar file to pass to a function
    that accepts a single pathlike object."""
    with tarfile.open(tarpath, "r") as tar:
        tar_member = tar.extractfile(filename)
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            shutil.copyfileobj(tar_member, tmp_file)
            tmp_file.flush()
            out = function(tmp_file.name, **kwargs)
    return out


def tar_wrapper_multiple(
    tarpath: str | Path,
    filenames: list[str],
    function: callable,
    **kwargs,
):
    """Wrapper for extracting multiple file objects from a tar file to pass to a function
    that accepts multiple pathlike objects."""
    tmp_filenames = []
    with tarfile.open(tarpath, "r") as tar:
        for filename in filenames:
            tar_member = tar.extractfile(filename)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(tar_member, tmp_file)
                tmp_file.close()
                tmp_filenames.append(tmp_file.name)

    if tmp_filenames:
        try:
            out = function(*tmp_filenames, **kwargs)
        finally:
            for tmp_file in tmp_filenames:
                os.remove(tmp_file)
    return out


def load_acetonitrile_spectra() -> tuple[list[RamanSpectrum], list[str]]:
    """Load acetonitrile spectra from each instrument."""
    # Map spectrometer info to file paths
    filepaths = {
        ("horiba", 785): DATA_DIRECTORY / "Horiba_MacroRAM/acetonitrile.txt",
        ("renishaw", 785): DATA_DIRECTORY / "Renishaw_Qontor/acetonitrile_5x.txt",
        ("wasatch", 785): DATA_DIRECTORY / "Wasatch_WP785X/acetonitrile.csv",
        ("openraman", 532): DATA_DIRECTORY / "OpenRAMAN/acetonitrile_n_n_n_solid_10000_0_5.csv",
        ("wasatch", 532): DATA_DIRECTORY / "Wasatch_WP532X/acetonitrile.csv",
    }
    openraman_neon_calibration = DATA_DIRECTORY / "OpenRAMAN/neon_n_n_n_solid_10000_0_5.csv"

    # Load spectra
    spectra = [
        RamanSpectrum.from_horiba_txtfile(filepaths[("horiba", 785)]),
        RamanSpectrum.from_renishaw_txtfile(filepaths[("renishaw", 785)]),
        RamanSpectrum.from_wasatch_csvfile(filepaths[("wasatch", 785)]),
        RamanSpectrum.from_openraman_csvfiles(
            filepaths[("openraman", 532)],
            openraman_neon_calibration,
            filepaths[("openraman", 532)],
        ),
        RamanSpectrum.from_generic_csvfile(filepaths[("wasatch", 532)]),
    ]

    # Convert spectrometer info into DataFrame
    dataframe = pd.DataFrame.from_records(list(filepaths.keys()), columns=["instrument", "λ_nm"])
    return spectra, dataframe


def load_cc124_tap_spectra() -> tuple[list[RamanSpectrum], list[str]]:
    """Load individual cell spectra from each instrument."""
    # Horiba
    txt_filepath = DATA_DIRECTORY / "Horiba_MacroRAM/CC-124-TAP-2.txt"
    horiba_spectrum = RamanSpectrum.from_horiba_txtfile(txt_filepath)

    # OpenRAMAN -- a bit special because it needs to be calibrated
    csv_filepath = DATA_DIRECTORY / "OpenRAMAN/CC-124_TAP_Pos-2-000_002.csv"
    openraman_calibration_files = [
        DATA_DIRECTORY / "OpenRAMAN/neon_n_n_n_solid_10000_0_5.csv",
        DATA_DIRECTORY / "OpenRAMAN/acetonitrile_n_n_n_solid_10000_0_5.csv",
    ]
    openraman_spectrum = RamanSpectrum.from_openraman_csvfiles(
        csv_filepath,
        *openraman_calibration_files,
    )

    # Renishaw -- a bit special because it comes from a multipoint scan, for which there is no
    # class method to automatically instantiate a `RamanSpectrum` object
    # There are 3 points to choose from, we will arbitrarily choose the first one
    txt_filepath = DATA_DIRECTORY / "Renishaw_Qontor/CC-124_TAP_plate_5x_3_points.txt"
    wavenumbers_cm1, intensities, _positions = read_renishaw_multipoint_txt(txt_filepath)
    renishaw_spectrum = RamanSpectrum(wavenumbers_cm1, intensities[0, :])

    # Wasatch 532 nm
    csv_filepath = DATA_DIRECTORY / "Wasatch_WP532X/CC-124_TAP_Pos-4-002_001.csv"
    wasatch_532_spectrum = RamanSpectrum.from_generic_csvfile(csv_filepath)

    # Wasatch 785 nm
    csv_filepath = DATA_DIRECTORY / "Wasatch_WP785X/CC-124_TAP_WP-02071.csv"
    wasatch_785_spectrum = RamanSpectrum.from_wasatch_csvfile(csv_filepath)

    # Compile spectra
    mapped_spectra = {
        ("horiba", 785): horiba_spectrum,
        ("renishaw", 785): renishaw_spectrum,
        ("wasatch", 785): wasatch_785_spectrum,
        ("openraman", 532): openraman_spectrum,
        ("wasatch", 532): wasatch_532_spectrum,
    }
    spectra = list(mapped_spectra.values())

    # Convert spectrometer info into DataFrame
    spectrometer_info = list(mapped_spectra.keys())
    dataframe = pd.DataFrame.from_records(spectrometer_info, columns=["instrument", "λ_nm"])
    return spectra, dataframe


def load_chlamy_spectra(data_directory: str) -> tuple[list[RamanSpectrum], pd.DataFrame]:
    """Load cell spectra from Wasatch 785 nm instrument."""
    pattern = "*-Site_*.csv"
    reader = RamanSpectrum.from_generic_csvfile

    spectra = []
    instrument_data = []
    wavelength_data = []
    well_id_data = []
    site_data = []

    # Loop through all the cell spectra within the directory
    for root, _, files in os.walk(data_directory):
        for filename in files:
            if fnmatch(filename, pattern):
                filepath = os.path.join(root, filename)

                # Infer well_ID and site from filename
                match = re.match(r"([A-H][1-9]|1[0-2])-Site_(\d+).csv", filename)
                if match:
                    well_id, site = match.groups()

                    # Load Wasatch spectra
                    spectrum = reader(filepath)
                    spectra.append(spectrum)
                    instrument_data.append("wasatch")
                    wavelength_data.append(785)
                    well_id_data.append(well_id)
                    site_data.append(site)

    # Create DataFrame in which to put instrument well_ID and site info corresponding to each spectrum
    data = {
        "instrument": instrument_data,
        "λ_nm": wavelength_data,
        "well_ID": well_id_data,
        "site": site_data,
    }
    dataframe = pd.DataFrame(data)
    return spectra, dataframe
