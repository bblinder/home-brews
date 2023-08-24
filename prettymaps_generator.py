#!/usr/bin/env python3

"""
Based on https://github.com/chrieke/prettymapp

Start with `pip install prettymapp`
"""

import argparse
import warnings

from prettymapp.geo import get_aoi
from prettymapp.osm import get_osm_geometries
from prettymapp.plotting import Plot
from prettymapp.settings import STYLES

# Suppress the specific FutureWarning related to set indexing
warnings.simplefilter(action="ignore", category=FutureWarning)
warnings.simplefilter(action="ignore", category=UserWarning)


def generate_map(address, radius, style, output_file):
    """
    Generate and save a map based on provided parameters.

    Args:
    - address (str): Address for the center of the Area of Interest (AOI).
    - radius (float): Radius for the AOI.
    - style (str): Style name for the plotting.
    - output_file (str): Output file path to save the plot.
    """
    try:
        aoi = get_aoi(address=address, radius=radius, rectangular=False)
        df = get_osm_geometries(aoi=aoi)

        fig = Plot(df=df, aoi_bounds=aoi.bounds, draw_settings=STYLES[style]).plot_all()

        fig.savefig(output_file)
        print(f"Map saved to {output_file}")

    except Exception as e:
        print(f"Error generating map: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate and save a map based on provided parameters."
    )

    parser.add_argument(
        "-a",
        "--address",
        type=str,
        required=True,
        help="Address for the center of the AOI.",
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=float,
        default=1100,
        help="Radius for the AOI. Default is 1100.",
    )
    parser.add_argument(
        "-s",
        "--style",
        type=str,
        choices=list(STYLES.keys()),
        default="Flannel",
        help="Style name for the plotting. Default is 'Flannel'.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="map.jpg",
        help="Output file path to save the plot. Default is 'map.jpg'.",
    )

    args = parser.parse_args()

    generate_map(args.address, args.radius, args.style, args.output)


if __name__ == "__main__":
    main()
