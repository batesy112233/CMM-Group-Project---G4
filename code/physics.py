"""
Physics calculation module
Calculates hydrodynamic coefficients and properties

"""
import numpy as np
import config
from config import BuoyProperties

""" Calculates hydrodynamic added mass """
def calculate_added_mass(buoy_diameter: float, buoy_height: float) -> float:
    
    buoy_radius = buoy_diameter / 2.0
    volume = np.pi * buoy_radius**2 * buoy_height
    m_added = config.C_a * config.RHO_WATER * volume
    return m_added

""" Estimates radiation damping coefficient at specific frequency """
def calculate_radiation_damping(buoy_diameter: float, omega_peak: float = 0.8) -> float:
    
    c_rad = (config.RHO_WATER * config.G * buoy_diameter**2) / (2.0 * omega_peak)
    return c_rad

""" Calculates viscous drag coefficient """
def calculate_viscous_drag_coefficient(buoy_diameter: float) -> float:
    
    C_d = 1.0  # Typical for bluff body
    area = np.pi * (buoy_diameter / 2.0)**2
    k_drag = 0.5 * config.RHO_WATER * C_d * area
    return k_drag

""" Create a BuoyProperties object with all calculated parameters """
def create_buoy_properties(diameter: float, height: float, eta_pto: float = 0.90) -> BuoyProperties:

    area = np.pi * (diameter / 2.0)**2
    k_hydrostatic = config.RHO_WATER * config.G * area
    m_added = calculate_added_mass(diameter, height)
    c_rad = calculate_radiation_damping(diameter)
    k_drag = calculate_viscous_drag_coefficient(diameter)
    
    return BuoyProperties(
        diameter=diameter,
        height=height,
        area=area,
        k_hydrostatic=k_hydrostatic,
        m_added=m_added,
        c_rad=c_rad,
        k_drag=k_drag,
        eta_pto=eta_pto
    )