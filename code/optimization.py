"""
Optimization module.
Defines the objective function for minimization.

"""
import numpy as np
import logging
import config  
from config import BuoyProperties
from simulation import run_simulation

""" Runs a full simulation ith a given set of parameters and returns a score to be minimized """
logger = logging.getLogger(__name__)

def objective_function(params: np.ndarray, buoy_props: BuoyProperties) -> float:
    
    m_buoy, c_pto = params
    
    # Check bounds
    if not (config.MASS_BOUNDS[0] <= m_buoy <= config.MASS_BOUNDS[1]):
        return config.OPTIMIZATION_PENALTY
    if not (config.DAMPING_BOUNDS[0] <= c_pto <= config.DAMPING_BOUNDS[1]):
        return config.OPTIMIZATION_PENALTY
    
    # Run simulation
    sol = run_simulation(m_buoy, c_pto, buoy_props)
    
    if not sol.success:
        logger.warning(f"ODE solver failed: {sol.message}")
        return config.OPTIMIZATION_PENALTY
    
    # Evaluate solution
    t_eval = np.linspace(config.WAVE_TIME[0], config.WAVE_TIME[-1], config.EVAL_POINTS)
    z = sol.sol(t_eval)[0]
    z_dot = sol.sol(t_eval)[1]
    
    # Check constraints
    if np.any(np.abs(z) > config.MAX_DISPLACEMENT):
        return config.OPTIMIZATION_PENALTY
    
    pto_force = np.abs(c_pto * z_dot)
    if np.any(pto_force > config.MAX_PTO_FORCE):
        return config.OPTIMIZATION_PENALTY
    
    # Calculate power (from steady state only)
    t_start = config.WAVE_TIME[0]
    steady_state_mask = t_eval > (t_start + config.STEADY_STATE_CUTOFF)
    z_dot_steady = z_dot[steady_state_mask]
    
    if len(z_dot_steady) == 0:
        return config.OPTIMIZATION_PENALTY
    
    # Mechanical power
    instant_power_mechanical = c_pto * (z_dot_steady**2)
    
    # Apply PTO efficiency
    if config.PTO_EFFICIENCY:
        instant_power_electrical = buoy_props.eta_pto * instant_power_mechanical
    else:
        instant_power_electrical = instant_power_mechanical
    
    avg_power = np.mean(instant_power_electrical)
    
    # Only prints if average power is non-negligable
    if avg_power > 1e-3:
        logger.info(f"Testing: m={m_buoy:.0f} kg, c={c_pto:.0f} Ns/m -> Power={avg_power/1000.0:.1f} kW")
    
    return -avg_power