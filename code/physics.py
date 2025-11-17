import numpy as np
from config import C_a, RHO_WATER, G

""" Calculates hydrodynamic added mass """
def calculate_added_mass(buoy_diameter, buoy_height):
    
    buoy_radius = buoy_diameter / 2.0
    volume = np.pi * buoy_radius**2 * buoy_height # Total volume of buoy apporximated as cylinder
    m_added = C_a * RHO_WATER * volume
    return m_added

""" Estimates radiation damping coefficient at specific frequency """
def calculate_radiation_damping(buoy_diameter, omega_peak=0.8):
    
    c_rad = (RHO_WATER * G * buoy_diameter**2) / (2.0 * omega_peak)
    return c_rad

""" Calculates lumped quadratic drag coefficient """
def calculate_viscous_drag_coefficient(buoy_diameter):
    
    C_d = 1.0 # Drag coefficient
    area = np.pi * (buoy_diameter / 2.0)**2
    k_drag = 0.5 * RHO_WATER * C_d * area
    return k_drag
