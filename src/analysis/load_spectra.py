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


def load_chlamy_spectra():
    """Load cell spectra from each instrument."""
    # Map out strain, media, species info
    strains = ["CC-124", "CC-125", "CC-1373"]
    media = ["MN", "TAP"]
    species = {
        "CC-124": "C. reinhardtii",
        "CC-125": "C. reinhardtii",
        "CC-1373": "C. smithii",
    }

    mapped_tarpaths = {
        ("openraman", 532): Path("data/OpenRAMAN/chlamy_spectra.tar"),
        ("wasatch", 532): Path("data/Wasatch_WP532X/chlamy_spectra.tar"),
        ("renishaw", 785): Path("data/Renishaw_Qontor/chlamy_spectra.tar"),
        ("wasatch", 785): Path("data/Wasatch_WP785X/chlamy_spectra.tar"),
    }
    mapped_patterns = {
        ("openraman", 532): "./chlamy_spectra/CC-*/Pos*.csv",
        ("wasatch", 532): "./chlamy_spectra/CC-*/Pos*.csv",
        ("renishaw", 785): "./chlamy_spectra/2024*_cells*.txt",
        ("wasatch", 785): "./chlamy_spectra/enlighten*.csv",
    }
    mapped_readers = {
        ("openraman", 532): RamanSpectrum.from_openraman_csvfiles,
        ("wasatch", 532): RamanSpectrum.from_generic_csvfile,
        ("renishaw", 785): read_renishaw_multipoint_txt,
        ("wasatch", 785): RamanSpectrum.from_wasatch_csvfile,
    }

    spectra = []
    instrument_data = []
    wavelength_data = []
    strain_data = []
    media_data = []
    # Big loopity loop through all the cell spectra within each tar file
    for (instrument, wavelength_nm), tarpath in mapped_tarpaths.items():
        pattern = mapped_patterns[(instrument, wavelength_nm)]
        reader = mapped_readers[(instrument, wavelength_nm)]
        with tarfile.open(tarpath, "r") as tar:
            for member in tar.getmembers():
                if fnmatch(member.name, pattern):
                    # Infer sample info from filepath
                    strain_matches = [re.search(strain, member.name) for strain in strains]
                    medium_matches = [re.search(medium, member.name) for medium in media]
                    strain = next(match for match in strain_matches if match is not None).group()
                    medium = next(match for match in medium_matches if match is not None).group()

                    # Load OpenRAMAN spectra
                    if instrument == "openraman":
                        spectrum = tar_wrapper_multiple(
                            tarpath=tarpath,
                            filenames=[
                                member.name,
                                "./chlamy_spectra/calibration_data/neon_4x.csv",
                                "./chlamy_spectra/calibration_data/acetonitrile_4x.csv",
                            ],
                            function=reader,
                        )
                        spectra.append(spectrum)
                        instrument_data.append(instrument)
                        wavelength_data.append(wavelength_nm)
                        strain_data.append(strain)
                        media_data.append(medium)

                    # Load Renishaw spectra
                    elif instrument == "renishaw":
                        wavenumbers_cm1, intensities, _positions = tar_wrapper_single(
                            tarpath=tarpath,
                            filename=member.name,
                            function=reader,
                        )
                        for i in range(intensities.shape[0]):
                            spectrum = RamanSpectrum(wavenumbers_cm1, intensities[i, :])
                            spectra.append(spectrum)
                            instrument_data.append(instrument)
                            wavelength_data.append(wavelength_nm)
                            strain_data.append(strain)
                            media_data.append(medium)

                    # Load Wasatch spectra
                    else:
                        spectrum = tar_wrapper_single(
                            tarpath=tarpath,
                            filename=member.name,
                            function=reader,
                        )
                        spectra.append(spectrum)
                        instrument_data.append(instrument)
                        wavelength_data.append(wavelength_nm)
                        strain_data.append(strain)
                        media_data.append(medium)

    # Create DataFrame in which to put instrument strain, species, and media info corresponding
    # to each spectrum
    data = {
        "instrument": instrument_data,
        "λ_nm": wavelength_data,
        "species": None,  # placeholder
        "strain": strain_data,
        "medium": media_data,
    }
    dataframe = pd.DataFrame(data)
    dataframe["species"] = dataframe["strain"].map(species)
    return spectra, dataframe
