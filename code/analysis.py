import numpy as np
from scipy.interpolate import CubicSpline
from dynamics import buoy_equation_of_motion_enhanced
from config import G

""" Analyzes optimal simulation to find peak acceleration of buoy """
def find_max_acceleration(t_eval, z_optimal, z_dot_optimal, m_buoy, c_pto, k_hydro, 
                        m_added, c_rad, k_drag, eta_pto):
    
    print("\n--- Max Acceleration Analysis ---")
    
    # Recalculates acceleration at every point in optimal simulation
    z_double_dot = np.array([
        # Call ODE function for each time step
        buoy_equation_of_motion_enhanced(t, [z, z_dot], m_buoy, c_pto, k_hydro, m_added, c_rad, k_drag, eta_pto)[1]
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
        # Define a helper function that returns jerk value at time t
        def jerk_func(t):
            return jerk_spline(t)

        try:
            # Starting guess for root at midpoint of interval
            t_mid = (t_eval[i] + t_eval[i+1]) / 2
            root_candidate = t_mid
            
            # Start iterations of Newton's method to find exact root (jerk = 0)
            for _ in range(5):
                j = jerk_func(root_candidate)
                j_prime = accel_spline.derivative(2)(root_candidate)
                
                # Check to avoid division by zero
                if abs(j_prime) > 1e-10:
                    # Newton's method step
                    root_candidate = root_candidate - j / j_prime
                else:
                    break # Stop if derivative is too small
                
                # Check if refined root is still inside original search interval
                if not (t_eval[i] <= root_candidate <= t_eval[i+1]):
                    root_candidate = t_mid # If outside interval reset to midpoint
                    break
            
            # Add refined root to the list
            jerk_roots.append(root_candidate)
        
        # Ignores any numerical errors during root finding
        except Exception as e:
            pass
    
    # Convert list to numpy array for easy filtering
    jerk_roots = np.array(jerk_roots)
    steady_state_mask = jerk_roots > (t_eval[0] + 50) # Ignore initial transient phase
    
    # Get only roots that occured during steady state period
    roots_steady = jerk_roots[steady_state_mask]
    # Get acceleration values at these exact peak times
    accel_at_roots = accel_spline(roots_steady)
    
    # Check if any steady state peaks were found
    if len(accel_at_roots) > 0:
        max_accel_idx = np.argmax(np.abs(accel_at_roots)) # Find index of peak with largest absolute value
        max_accel_value = accel_at_roots[max_accel_idx] # Get actual acceleration value at that peak
        max_accel_time = roots_steady[max_accel_idx] # Get the time that peak occured
        
        # Print final result in m/s^2 and G-forces
        print(f"Max Acceleration: {max_accel_value:.2f} m/s² ({max_accel_value/G:.2f} G)")
        print(f"Time: {max_accel_time:.2f} s")
        
        # Return time and value of max acceleration
        return max_accel_time, max_accel_value
    else:
        # If no peaks were found in steady state
        print("Could not find significant acceleration peaks.")
        return None, None
        
