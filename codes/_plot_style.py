import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
import copy
import re
import xml.etree.ElementTree as ET


STYLE = {
    "legend.loc": "best",
    "font.size": 8,
    "scatter.edgecolors": "k",
    "scatter.marker": "o",
    "lines.linewidth": 0.5,
    "lines.markeredgewidth": 0.6,
    "patch.linewidth": 0.5,
    "savefig.dpi": 600,
    "savefig.transparent": False,
    "savefig.bbox": "tight",
    "mathtext.default": "regular",
    "figure.figsize": (3.5, 3.5),
}


C = {
    "figure_bg": "#FFFFFF",
    "axes_bg": "#FFFFFF",

    "blue": "#1455C0",
    "blue1": "#E0EFFB",
    "blue2": "#B4D5F6",
    "blue3": "#73AEF4",
    "blue4": "#347DE0",
    "blue5": "#1455C0",
    "blue6": "#0C3992",
    "blue7": "#0A1E6E",
    "blue8": "#061350",

    "green": "#408335",
    "green1": "#E2F3E5",
    "green2": "#BDDBB9",
    "green3": "#8CBC80",
    "green4": "#66A558",
    "green5": "#408335",
    "green6": "#2A7230",
    "green7": "#165C27",
    "green8": "#154A26",

    "lgreen": "#63A615",
    "lgreen1": "#EBF7DD",
    "lgreen2": "#C9EB9E",
    "lgreen3": "#9FD45F",
    "lgreen4": "#78BE14",
    "lgreen5": "#63A615",
    "lgreen6": "#508B1B",
    "lgreen7": "#44741A",
    "lgreen8": "#375F15",

    "red": "#EC0016",
    "red1": "#FEE6E6",
    "red2": "#FCC8C3",
    "red3": "#FA9090",
    "red4": "#F75056",
    "red5": "#EC0016",
    "red6": "#C50014",
    "red7": "#9B000E",
    "red8": "#740009",

    "yellow": "#FFD800",
    "orange": "#FF7A00",
    "yellow1": "#FFFFDC",
    "yellow2": "#FFFFAF",
    "yellow3": "#FFF876",
    "yellow4": "#FFF000",
    "yellow5": "#FFD800",
    "yellow6": "#FFBB00",
    "yellow7": "#FF9B00",
    "yellow8": "#FF7A00",

    "gray": "#7D7D7D",
    "black": "#000000",
    "white": "#FFFFFF",

    "wgray": "#858379",
    "wgray1": "#F5F4F1",
    "wgray2": "#DDDED6",
    "wgray3": "#BCBBB2",
    "wgray4": "#9C9A8E",
    "wgray5": "#858379",
    "wgray6": "#747067",
    "wgray7": "#4F4B41",
    "wgray8": "#38342F",

    "cgray": "#646973",
    "cgray1": "#F0F3F5",
    "cgray2": "#D7DCE1",
    "cgray3": "#AFB4BB",
    "cgray4": "#878C96",
    "cgray5": "#646973",
    "cgray6": "#3C414B",
    "cgray7": "#282D37",
    "cgray8": "#131821",

}


def apply_plot_style():
    plt.rcParams.update(STYLE)


def setup_axes(fig):
    for ax in fig.get_axes():
        ax.set_facecolor(C["axes_bg"])
        ax.set_axisbelow(True)

    if len(fig.get_axes()) > 1:
        for x in fig.get_axes():
            i = fig.get_axes().index(x)
            x.text(0.025, 0.975, chr(97 + i),
                    size=12, weight="bold", ha="left", va="top",
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=0.1, boxstyle='round'),
                    transform=x.transAxes)


def add_standard_legend(ax, **overrides):
    legend_options = {
        "loc": "upper left",
        "markerscale": 1,
        "frameon": True,
        "fancybox": False,
        "edgecolor": "black",
        "facecolor": "none",
        "framealpha": 1.0,
    }
    legend_options.update(overrides)
    ax.legend(**legend_options)


def save_figure(
    fig: plt.Figure, figures_dir: str | Path, filename: str,
    fixed_layout: bool = False,
) -> None:
    figures_dir = Path(figures_dir)
    if not (figures_dir / "png").exists():
        (figures_dir / "png").mkdir(parents=True)
    if not (figures_dir / "svg").exists():
        (figures_dir / "svg").mkdir(parents=True)

    if fixed_layout:
        # Preserve explicit margins and canvas size when optional artists change.
        with plt.rc_context({"savefig.bbox": None}):
            fig.savefig(figures_dir / "png" / f"{filename}.png")
            fig.savefig(figures_dir / "svg" / f"{filename}.svg")

    else:
        fig.tight_layout()
        fig.savefig(figures_dir / "png" / f"{filename}.png")
        fig.savefig(figures_dir / "svg" / f"{filename}.svg")
    plt.close(fig)