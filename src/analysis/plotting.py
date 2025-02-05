import arcadia_pycolor as apc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from numpy.typing import NDArray
from ramanalysis import RamanSpectrum

FloatArray = NDArray[np.float64]


def get_universal_colorpalette() -> dict[str | tuple[str, str], str]:
    # color palette for each instrument
    instrument_color_palette = {
        "openraman": apc.aegean.hex_code,
        "horiba": apc.amber.hex_code,
        "renishaw": apc.seaweed.hex_code,
        "wasatch": apc.aster.hex_code,
        "openraman_dark": "#315378",
        "horiba_dark": "#A65A42",
        "renishaw_dark": "#1E4D43",
        "wasatch_dark": "#43425E",
    }

    # color palette for each (strain, medium) combination
    chlamy_color_palette = {
        ("CC-124", "TAP"): apc.tangerine.hex_code,
        ("CC-125", "TAP"): apc.dragon.hex_code,
        ("CC-1373", "TAP"): apc.redwood.hex_code,
        ("CC-124", "MN"): apc.aegean.hex_code,
        ("CC-125", "MN"): apc.lapis.hex_code,
        ("CC-1373", "MN"): apc.lilac.hex_code,
    }

    # merge palettes
    color_palette = {**instrument_color_palette, **chlamy_color_palette}
    return color_palette


def get_default_plotly_layout(
    num_xaxes: int = 1,
    num_yaxes: int = 1,
    title: str = "Title",
    xaxis_title: str = "Wavenumber (cm^-1)",
) -> dict:
    axes_layout = {
        "gridcolor": apc.gray.hex_code,
        "linecolor": apc.black.hex_code,
        "ticks": "outside",
    }
    layout = {
        "grid": {"rows": num_yaxes, "columns": num_xaxes},
        "hoversubplots": "axis",
        "title": title,
        "xaxis_title": xaxis_title,
        "plot_bgcolor": apc.white.hex_code,
    }
    for n in range(num_xaxes):
        layout[f"xaxis{n + 1}"] = axes_layout
    for n in range(num_yaxes):
        layout[f"yaxis{n + 1}"] = axes_layout
    return layout


def generate_spectral_resolution_plot(
    spectra: list[RamanSpectrum],
    dataframe: pd.DataFrame,
    labels: None | list[str],
) -> go.Figure:
    """Generate an interactive plotly visualization to assess spectral resolution."""
    color_palette = get_universal_colorpalette()
    plots = []

    # generate plots for spectra
    for i, spectrum in enumerate(spectra):
        plot_spectrum = go.Scatter(
            x=spectrum.wavenumbers_cm1,
            y=spectrum.normalize().intensities,
            yaxis=f"y{i + 1}",
            name=labels[i],
            hoverinfo="skip",
            marker={"color": color_palette[labels[i]]},
        )
        plots.append(plot_spectrum)

        # TODO: make this make sense or at least explain assumptions
        peaks_subset = dataframe.loc[dataframe["instrument"] == labels[i]].drop(
            ["instrument", "sigma", "gamma"], axis=1
        )
        # generate plots for peaks
        for _row_id, row in peaks_subset.iterrows():
            # annotate each peak with parameters of the best fit
            annotation_text = [k + ": " + f"{v:.3g}<br>" for k, v in row.to_dict().items()]
            # marker with annotation for each peak
            plot_peaks = go.Scatter(
                x=[row["center"]],
                y=[row["height"]],
                yaxis=f"y{i + 1}",
                name=labels[i],
                showlegend=False,
                hovertext="".join(annotation_text),
                marker={"color": color_palette[f"{labels[i]}_dark"]},
            )
            plots.append(plot_peaks)

    # get figure layout
    layout = get_default_plotly_layout(
        num_yaxes=len(spectra),
        title="Acetonitrile spectra",
    )
    fig = go.Figure(data=plots, layout=layout)
    return fig


def generate_baseline_estimation_plot(
    spectra: list[RamanSpectrum],
    baselines: list[FloatArray],
    labels: None | list[str],
    title: None | str,
) -> go.Figure:
    """Generate an interactive plotly visualization to ."""
    color_palette = get_universal_colorpalette()
    plots = []

    for i, (spectrum, baseline) in enumerate(zip(spectra, baselines, strict=True)):
        # plot spectrum
        plot_spectrum = go.Scatter(
            x=spectrum.wavenumbers_cm1,
            y=spectrum.normalize().intensities,
            yaxis=f"y{i + 1}",
            name=labels[i],
            hoverinfo="skip",
            marker={"color": color_palette[labels[i]]},
        )

        # plot baseline
        plot_baseline = go.Scatter(
            x=spectrum.wavenumbers_cm1,
            y=baseline,
            yaxis=f"y{i + 1}",
            showlegend=False,
            hoverinfo="skip",
            marker={"color": color_palette[f"{labels[i]}_dark"]},
        )
        plots.append(plot_baseline)
        plots.append(plot_spectrum)

    # get figure layout
    layout = get_default_plotly_layout(
        num_yaxes=len(spectra),
        title=title,
    )
    fig = go.Figure(data=plots, layout=layout)
    return fig


def generate_snr_measurement_plot(
    spectra: list[RamanSpectrum],
    peaks: list[tuple[FloatArray, FloatArray]],
    snr_measurements: list[float],
    labels: None | list[str],
    title: None | str,
) -> go.Figure:
    """Generate an interactive plotly visualization to ."""
    color_palette = get_universal_colorpalette()
    plots = []

    for i, (spectrum, (peaks_cm1, peak_heights)) in enumerate(zip(spectra, peaks, strict=True)):
        # plot spectrum
        plot_spectrum = go.Scatter(
            x=spectrum.wavenumbers_cm1,
            y=spectrum.normalize().intensities,
            yaxis=f"y{i + 1}",
            name=labels[i],
            hoverinfo="skip",
            marker={"color": color_palette[labels[i]]},
        )
        plots.append(plot_spectrum)

        # plot peaks
        plot_peaks = go.Scatter(
            x=peaks_cm1,
            y=peak_heights,
            yaxis=f"y{i + 1}",
            mode="markers",
            name=labels[i],
            showlegend=False,
            marker={"color": color_palette[f"{labels[i]}_dark"]},
        )
        plots.append(plot_peaks)

    # get figure layout
    layout = get_default_plotly_layout(
        num_yaxes=len(spectra),
        title=title,
    )
    fig = go.Figure(data=plots, layout=layout)
    return fig
