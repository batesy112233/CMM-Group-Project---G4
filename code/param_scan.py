"""
param_scan.py

Parameter sweep script for the wave energy buoy model.

This script:
  1. Loads the wave elevation data and creates the buoy properties.
  2. Sweeps buoy mass (within MASS_BOUNDS) and PTO damping (within a valid range).
  3. Evaluates the average electrical power using the existing objective_function.
  4. Filters out penalised (invalid) cases.
  5. Plots power vs mass:
        - 8 PTO damping values in total (monotonically increasing),
        - split into 2 figures, each showing 4 damping curves.
"""

import sys
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import config
from config import OPTIMIZATION_PENALTY
from wave_processing import analyze_and_prepare_wave_data
from physics import create_buoy_properties
from optimization import objective_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def plot_power_curves(df: pd.DataFrame, damping_subset, title: str):
    """
    Plot power vs mass for a subset of PTO damping values.

    Parameters
    ----------
    df : pandas.DataFrame
        Must contain columns: 'mass', 'damping', 'power' (kW).
    damping_subset : list or array of float
        The damping values to include in this figure.
    title : str
        Title of the figure.
    """
    plt.figure(figsize=(8, 6))

    for c in damping_subset:
        group = df[df["damping"] == c].sort_values("mass")

        if group.empty:
            continue  # No valid points for this damping

        plt.plot(
            group["mass"],
            group["power"],
            marker="o",
            linestyle="-",
            label=f"c = {c:,.0f} Ns/m",
        )

    plt.xlabel("Buoy mass (kg)")
    plt.ylabel("Average electrical power (kW)")
    plt.title(title)
    plt.grid(True)
    plt.legend(title="PTO damping")
    plt.tight_layout()
    plt.show()


def main():
    # ---------------------------------------------------------
    # 1. Load and preprocess wave data
    # ---------------------------------------------------------
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "wave_elevation_data.csv"
        logger.info(f"No file path provided, using default: {file_path}")

    if not analyze_and_prepare_wave_data(file_path, dt_step=0.1):
        logger.error("Failed to load wave data. Exiting.")
        sys.exit(1)

    # ---------------------------------------------------------
    # 2. Create buoy properties (same as in main.py)
    # ---------------------------------------------------------
    buoy_props = create_buoy_properties(diameter=8.0, height=6.0, eta_pto=0.90)
    logger.info("Buoy properties created for parameter sweep.")

    # ---------------------------------------------------------
    # 3. Define the parameter ranges for the sweep
    # ---------------------------------------------------------
    # Mass range: from MASS_BOUNDS, using 7 evenly spaced points
    masses = np.linspace(config.MASS_BOUNDS[0],
                         config.MASS_BOUNDS[1],
                         7)

#We select 1e5 Ns/m as the lower bound for 'valid' damping because
#PTO damping below 1×10^5 Ns/m causes large-amplitude buoy motion,
#resulting in constraint violations (excessive displacement or excessive PTO force).
#Starting from approximately 1×10^5 Ns/m, ALL mass values in the range
#20,000–200,000 kg remain physically feasible.

    valid_damping_min = 1.0e5
    valid_damping_max = 9.0e5
    dampings = np.linspace(valid_damping_min, valid_damping_max, 8)

    logger.info(f"Scanning masses:   {masses}")
    logger.info(f"Scanning dampings: {dampings}")

    mass_values = []
    damping_values = []
    power_values = []

    # ---------------------------------------------------------
    # 4. Parameter sweep: for each (mass, damping) evaluate power
    # ---------------------------------------------------------
    for c in dampings:
        for m in masses:
            x = [m, c]

            f_val = objective_function(x, buoy_props)

            # Skip penalised (invalid) cases
            if f_val >= OPTIMIZATION_PENALTY * 0.5:
                logger.warning(
                    f"Skipping penalised case m={m:.0f} kg, c={c:.0f} Ns/m "
                    f"(objective = {f_val:.2e})"
                )
                continue

            # objective_function returns -avg_power in Watts
            power_W = -f_val
            power_kW = power_W / 1000.0

            logger.info(
                f"Recorded: m={m:.0f} kg, c={c:.0f} Ns/m -> Power={power_kW:.1f} kW"
            )

            mass_values.append(m)
            damping_values.append(c)
            power_values.append(power_kW)

    # ---------------------------------------------------------
    # 5. Build DataFrame and generate two figures
    # ---------------------------------------------------------
    if len(mass_values) == 0:
        logger.error("No valid (mass, damping) combinations were found!")
        return

    df = pd.DataFrame({
        "mass": mass_values,
        "damping": damping_values,
        "power": power_values,
    })

    # Sort and split the 8 damping values into two groups of 4
    unique_dampings = sorted(df["damping"].unique())
    if len(unique_dampings) < 8:
        logger.warning(
            f"Expected 8 unique damping values, but found {len(unique_dampings)}."
        )

    first_half = unique_dampings[:4]
    second_half = unique_dampings[4:]

    # First figure: lower half of the damping range
    plot_power_curves(
        df,
        first_half,
        title="Average power vs mass (lower PTO damping range)"
    )

    # Second figure: upper half of the damping range
    plot_power_curves(
        df,
        second_half,
        title="Average power vs mass (higher PTO damping range)"
    )


if __name__ == "__main__":
    main()




