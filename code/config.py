"""

Configuration module for Wave Energy Buoy Optimization.
Contains constants and shared data structures

"""
import numpy as np
from dataclasses import dataclass

# Constants
G = 9.81
RHO_WATER = 1025.0 # Density of sea-water
C_a = 0.5 # Added mass coefficient

# On/off switches to toggle various physical parameters
HYDRODYNAMIC_MASS = True # Include weight of water stuck to buoy
RADIATION_DAMPING = True # Include damping from buoy making its own waves
VISCOUS_DRAG = True # Include damping from water friction (drag)
PTO_EFFICIENCY = True # Include how efficient the power generator is

# Optimization constants
OPTIMIZATION_PENALTY = 1e10
STEADY_STATE_CUTOFF = 50.0  # seconds
EVAL_POINTS = 2000
MAX_TIMESTEP = 0.5          # seconds

# Minimum and maximum values to test
MASS_BOUNDS = (20000.0, 200000.0) # (min_mass, max_mass) in kg
DAMPING_BOUNDS = (10000.0, 1000000.0) # (min_damping, max_damping)

# Physical Limits of buoy
MAX_DISPLACEMENT = 3.5 # Max distance the buoy can move vertically (meters)
MAX_PTO_FORCE = 1_500_000.0 # Max force the generator can withstand (Newtons)

# Generate lists to be filled with data from wave data file

# For high detail wave data (resampled)
WAVE_TIME = np.array([])
WAVE_VERTICAL_DISPLACEMENT = np.array([])

# For original, low detail wave data
WAVE_TIME_COARSE = np.array([])
WAVE_VERTICAL_DISPLCEMENT_COARSE = np.array([])
wave_interp = None  # Will hold interpolation function

# Data Classes
""" Container for buoy physical properties """
@dataclass
class BuoyProperties:
    
    diameter: float         # meters
    height: float           # meters (draft)
    area: float            # m^2
    k_hydrostatic: float   # N/m
    m_added: float         # kg
    c_rad: float           # Ns/m
    k_drag: float          # kg/m
    eta_pto: float         # efficiency (0-1)