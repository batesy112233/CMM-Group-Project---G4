"""
Analysis module.
Post-processing functions like acceleration analysis.

"""
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
import logging
from typing import Optional, Tuple
import config
from config import BuoyProperties
from dynamics import buoy_equation_of_motion

logger = logging.getLogger(__name__)

""" Analyzes optimal simulation to find peak acceleration of buoy """
def find_max_acceleration(t_eval: np.ndarray, z_optimal: np.ndarray, 
                         z_dot_optimal: np.ndarray, m_buoy: float, 
                         c_pto: float, buoy_props: BuoyProperties) -> Tuple[Optional[float], Optional[float]]:
    
    logger.info("Finding maximum acceleration...")
 
    try:
        # Recalculates acceleration at every point in optimal simulation
        z_double_dot = np.array([
            # Call ODE function for each time step
            buoy_equation_of_motion(t, [z, z_dot], m_buoy, c_pto, buoy_props)[1]
            for t, z, z_dot in zip(t_eval, z_optimal, z_dot_optimal)
        ])
    
        # Create continuous spline function from discrete acceleration points
        accel_spline = CubicSpline(t_eval, z_double_dot)
        jerk_spline = accel_spline.derivative()
    
        # Evaluates the jerk (derivative of acceleration) at each time step 
        jerk_values = jerk_spline(t_eval)
        sign_changes = np.where(np.diff(np.sign(jerk_values)))[0]
        
        # List for times of acceleration peaks
        jerk_roots = []
    
        # Loop through each location where the sign changed 
        for i in sign_changes:
            try:
                root = brentq(jerk_spline, t_eval[i], t_eval[i+1], xtol=1e-6)
                jerk_roots.append(root)
            except ValueError:
                pass  # No root in this interval
        
        if len(jerk_roots) == 0:
            logger.warning("No jerk roots found")
            return None, None
        
        # Filter to steady state
        jerk_roots = np.array(jerk_roots)
        steady_mask = jerk_roots > (t_eval[0] + config.STEADY_STATE_CUTOFF)
        roots_steady = jerk_roots[steady_mask]
        
        if len(roots_steady) == 0:
            logger.warning("No jerk roots in steady state region")
            return None, None
        
        # Find maximum acceleration
        accel_at_roots = accel_spline(roots_steady)
        max_idx = np.argmax(np.abs(accel_at_roots))
        max_accel = accel_at_roots[max_idx]
        max_time = roots_steady[max_idx]
        
        logger.info(f"Max acceleration: {max_accel:.2f} m/s² ({max_accel/config.G:.2f} G) at t={max_time:.2f}s")
        return max_time, max_accel
        
    except Exception as e:
        logger.error(f"Error finding max acceleration: {type(e).__name__}: {str(e)}")
        return None, None
        
