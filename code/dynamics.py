"""
Dynamics module
Defines the equation of motion for the buoy

"""
import numpy as np
import config
from config import BuoyProperties
from wave_processing import create_forcing_function

""" Buoy equation of motion with enhanced physics """
def buoy_equation_of_motion(t: float, y: np.ndarray, m_buoy: float, c_pto: float, 
                           buoy_props: BuoyProperties) -> list:
    
    z, z_dot = y
    
    # Total effective mass
    m_total = m_buoy + buoy_props.m_added
    
    # Calculate forces
    F_wave = create_forcing_function(t, buoy_props.k_hydrostatic)
    F_hydrostatic = -buoy_props.k_hydrostatic * z
    F_pto = -c_pto * z_dot
    
    F_radiation = -buoy_props.c_rad * z_dot if config.RADIATION_DAMPING else 0.0
    F_drag = -buoy_props.k_drag * np.abs(z_dot) * z_dot if config.VISCOUS_DRAG else 0.0
    
    # Total force and acceleration
    F_total = F_wave + F_hydrostatic + F_pto + F_radiation + F_drag
    z_double_dot = F_total / m_total
    
    return [z_dot, z_double_dot]
