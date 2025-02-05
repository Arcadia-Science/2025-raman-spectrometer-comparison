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
    # Specify file paths
    mapped_filepaths = {
        "horiba": DATA_DIRECTORY / "Horiba_MacroRAM/acetonitrile.txt",
        "openraman": DATA_DIRECTORY / "OpenRAMAN/acetonitrile_n_n_n_solid_10000_0_5.csv",
        "renishaw": DATA_DIRECTORY / "Renishaw_Qontor/acetonitrile_5x.txt",
        "wasatch": DATA_DIRECTORY / "Wasatch_WP785X/acetonitrile.csv",
    }
    openraman_neon_calibration = DATA_DIRECTORY / "OpenRAMAN/neon_n_n_n_solid_10000_0_5.csv"

    # Compile spectra
    mapped_spectra = {
        "horiba": RamanSpectrum.from_horiba_txtfile(mapped_filepaths["horiba"]),
        "openraman": RamanSpectrum.from_openraman_csvfiles(
            mapped_filepaths["openraman"],
            openraman_neon_calibration,
            mapped_filepaths["openraman"],
        ),
        "renishaw": RamanSpectrum.from_renishaw_txtfile(mapped_filepaths["renishaw"]),
        "wasatch": RamanSpectrum.from_wasatch_csvfile(mapped_filepaths["wasatch"]),
    }
    instruments = list(mapped_spectra.keys())
    spectra = list(mapped_spectra.values())
    return spectra, instruments


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

    # Wasatch
    csv_filepath = DATA_DIRECTORY / "Wasatch_WP785X/CC-124_TAP_WP-02071.csv"
    wasatch_spectrum = RamanSpectrum.from_wasatch_csvfile(csv_filepath)

    # Compile spectra
    mapped_spectra = {
        "horiba": horiba_spectrum,
        "openraman": openraman_spectrum,
        "renishaw": renishaw_spectrum,
        "wasatch": wasatch_spectrum,
    }
    instruments = list(mapped_spectra.keys())
    spectra = list(mapped_spectra.values())
    return spectra, instruments


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
        "horiba": Path("data/Horiba_MacroRAM/chlamy_spectra.tar"),
        "openraman": Path("data/OpenRAMAN/chlamy_spectra.tar"),
        "renishaw": Path("data/Renishaw_Qontor/chlamy_spectra.tar"),
        "wasatch": Path("data/Wasatch_WP785X/chlamy_spectra.tar"),
    }
    mapped_patterns = {
        "horiba": "./chlamy_spectra/CC*.txt",
        "openraman": "./chlamy_spectra/CC-*/Pos*.csv",
        "renishaw": "./chlamy_spectra/2024*_cells*.txt",
        "wasatch": "./chlamy_spectra/enlighten*.csv",
    }
    mapped_readers = {
        "horiba": RamanSpectrum.from_horiba_txtfile,
        "openraman": RamanSpectrum.from_openraman_csvfiles,
        "renishaw": read_renishaw_multipoint_txt,
        "wasatch": RamanSpectrum.from_wasatch_csvfile,
    }

    spectra = []
    instrument_data = []
    strain_data = []
    media_data = []
    # Big loopity loop through all the cell spectra within each tar file
    for instrument, tarpath in mapped_tarpaths.items():
        pattern = mapped_patterns[instrument]
        reader = mapped_readers[instrument]
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
                            strain_data.append(strain)
                            media_data.append(medium)

                    # Load Horiba and Wasatch spectra
                    else:
                        spectrum = tar_wrapper_single(
                            tarpath=tarpath,
                            filename=member.name,
                            function=reader,
                        )
                        spectra.append(spectrum)
                        instrument_data.append(instrument)
                        strain_data.append(strain)
                        media_data.append(medium)

    # Create DataFrame in which to put instrument strain, species, and media info corresponding
    # to each spectrum
    data = {
        "instrument": instrument_data,
        "species": None,  # placeholder
        "strain": strain_data,
        "medium": media_data
    }
    dataframe = pd.DataFrame(data)
    dataframe["species"] = dataframe["strain"].map(species)
    return spectra, dataframe
