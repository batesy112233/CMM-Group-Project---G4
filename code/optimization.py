import numpy as np
from scipy.integrate import solve_ivp
from config import *
from dynamics import buoy_equation_of_motion_enhanced

""" Runs a full simulatoin ith a given set of parameters and returns a score to be minimized """
def objective_function_enhanced(params, k_hydro, m_added, c_rad, k_drag, eta_pto):
    
    m_buoy, c_pto = params
    
    # Parameters bounds check
    if not (MASS_BOUNDS[0] <= m_buoy <= MASS_BOUNDS[1]):
        return 1e10 # Returns large penalty if mass is out of bounds
    
    if not (DAMPING_BOUNDS[0] <= c_pto <= DAMPING_BOUNDS[1]):
        return 1e10 # Returns large penalty if damping is out of bounds
    
    # Simulation Setup
    t_span = [WAVE_TIME[0], WAVE_TIME[-1]] # Define time range
    y0 = [0, 0] # Define initial conditions
    
    # Run simulation
    try:
        # Calling the ODE solver with the physics function and all parameters
        sol = solve_ivp(
            buoy_equation_of_motion_enhanced,
            t_span,
            y0,
            method='RK45', # Runge-Kutta 4/5
            args=(m_buoy, c_pto, k_hydro, m_added, c_rad, k_drag, eta_pto),
            dense_output=True,
            max_step=0.5
        )
        
        # Checks if solver reports a failure
        if not sol.success:
            return 1e10 # Returns Large Penalty
        
    # Catch any other errors during simulation    
    except Exception as e:
        return 1e10 # Return a large penalty
    
    # Analyse the simulation results
    t_eval = np.linspace(t_span[0], t_span[1], 2000)
    z = sol.sol(t_eval)[0]
    z_dot = sol.sol(t_eval)[1]  
    
    pto_force = np.abs(c_pto * z_dot) # Calculate instantaneous force on PTO system
    
    # Check if buoy position exceeds physical limit
    if np.any(np.abs(z) > MAX_DISPLACEMENT):
        return 1e10 # REturn large penalty
    
    # Check if PTO force exceeded mechanical force limit
    if np.any(pto_force > MAX_PTO_FORCE):
        return 1e10 # Return large penalty
    
    # Calculate average power
    steady_state_mask = t_eval > (t_span[0] + 50) # Ignores initial transient phase
    z_dot_steady = z_dot[steady_state_mask]
    
    # If simulation shorter than 50s use full dataset
    if len(z_dot_steady) == 0:
        z_dot_steady = z_dot
    
    # Check if z_dot still empty (e.g. simulation failed instantly)
    if len(z_dot_steady) == 0:
        return 1e10
    
    # Calculate instantaneous mechanical power
    instant_power_mechanical = c_pto * (z_dot_steady**2)
    
    # Apply PTO efficiency from config file
    if PTO_EFFICIENCY:
        instant_power_electrical = eta_pto * instant_power_mechanical
    else:
        instant_power_electrical = instant_power_mechanical
    
    # Calculate avergae power for steady state period
    avg_power = np.mean(instant_power_electrical)
    
    # Only prints if power is non-negligable
    if avg_power > 1e-3: 
        print(f"Testing: m={m_buoy:.0f} kg, c={c_pto:.0f} Ns/m -> Power={avg_power/1000.0:.1f} kW")
    
    # Return final score
    return -avg_power
