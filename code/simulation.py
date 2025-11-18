"""
Simulation module.
Handles the execution of the ODE solver.

"""
import numpy as np
from scipy.integrate import solve_ivp
import logging
import config
from dynamics import buoy_equation_of_motion
from config import BuoyProperties

logger = logging.getLogger(__name__)

""" Runs the buoy simulation using scipy.integrate.solve_ivp """
def run_simulation(m_buoy: float, c_pto: float, buoy_props: BuoyProperties):
   
    # Define time span based on loaded wave data
    t_span = [config.WAVE_TIME[0], config.WAVE_TIME[-1]]
    y0 = [0.0, 0.0] # Initial conditions [z, z_dot]

    try:
        sol = solve_ivp(
            buoy_equation_of_motion,
            t_span,
            y0,
            method='RK45',
            args=(m_buoy, c_pto, buoy_props),
            dense_output=True,
            max_step=config.MAX_TIMESTEP
        )
        return sol
    
    # Return a dummy object with success=False to handle error
    except Exception as e:
        logger.error(f"Simulation failed inside run_simulation: {type(e).__name__}: {str(e)}")
        class FailedSolution:
            success = False
            message = str(e)
        return FailedSolution()