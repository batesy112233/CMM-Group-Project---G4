import numpy as np
from scipy.optimize import minimize
from scipy.integrate import solve_ivp
import sys

# Import all functions and variables from other files
from config import *
from wave_processing import analyze_and_prepare_wave_data, create_forcing_function
from physics import calculate_added_mass, calculate_radiation_damping, calculate_viscous_drag_coefficient
from dynamics import buoy_equation_of_motion_enhanced
from optimization import objective_function_enhanced
from analysis import find_max_acceleration
from visualization import plot_results_enhanced

if __name__ == "__main__":
    
    # Initialize and load data
    print("="*60)
    print("WAVE ENERGY BUOY OPTIMIZATION")
    print("="*60)
    
    # Call function to read, clean and resample the wave data
    try:
        analyze_and_prepare_wave_data(dt_step=0.1)
    except Exception as e:
        print(f"Could not analyze wave data: {e}")
        sys.exit(1)
    
    # Calculate fixed physical parameters
    buoy_diameter = 8.0
    buoy_height = 6.0
    
    # Calculate waterplane area assuming a cylinder
    buoy_area = np.pi * (buoy_diameter / 2.0)**2
    
    # Calculate the hydrostatic stiffness
    k_hydrostatic = RHO_WATER * G * buoy_area
    
    # Calculate hydrodynamiccoefficients based on geometry 
    m_added = calculate_added_mass(buoy_diameter, buoy_height)
    c_rad = calculate_radiation_damping(buoy_diameter, omega_peak=0.8)
    k_drag = calculate_viscous_drag_coefficient(buoy_diameter)
    eta_pto = 0.90
    
    # print calculated parameters to the console
    print(f"\nBuoy Diameter: {buoy_diameter} m")
    print(f"Added mass: {m_added:.0f} kg")
    print(f"Radiation damping: {c_rad:.0f} Ns/m")
    print(f"Drag coefficient: {k_drag:.2f} kg/m")
    
    # Setup the optimization
    x0 = [np.mean(MASS_BOUNDS), np.mean(DAMPING_BOUNDS)]
    bounds = [MASS_BOUNDS, DAMPING_BOUNDS]
    
    print("\nStarting optimization...")
    
    # Call the minimize function to find best parameters
    result = minimize(
        objective_function_enhanced,
        x0,
        args=(k_hydrostatic, m_added, c_rad, k_drag, eta_pto),
        method='Nelder-Mead',
        options={'xatol': 1e-3, 'fatol': 1.0, 'disp': True, 'maxiter': 200} # Optomizer settings
    )
    
    # Process and display results
    if result.success:
        # Get optimal parameters from result
        opt_mass, opt_damping = result.x
        max_power_electrical = -result.fun # Flip sign since -power was minimized
        
        # Print final optimal values
        print(f"\nOptimal Mass: {opt_mass:.0f} kg")
        print(f"Optimal Damping: {opt_damping:.0f} Ns/m")
        print(f"Electrical Power: {max_power_electrical / 1000.0:.2f} kW")
        
        # Re-run final simulation for plotting
        t_span = [WAVE_TIME[0], WAVE_TIME[-1]] # Set time range
        t_eval = np.linspace(t_span[0], t_span[1], 5000) 
        y0 = [0, 0] # Set initial conditions
        
        # Run ODE solver with optimal parameters
        sol_optimal = solve_ivp(
            buoy_equation_of_motion_enhanced, # Physics function
            t_span, # Time range
            y0, # Initial state
            method='RK45', # Use runge-kutta sovler
            args=(opt_mass, opt_damping, k_hydrostatic, m_added, c_rad, k_drag, eta_pto),
            t_eval=t_eval,
            max_step=0.5 # Limits time step for stability
        )
        
        # If final simulation was succesful
        if sol_optimal.success:
            # Extract position and velocity from the solution
            z_optimal = sol_optimal.y[0]
            z_dot_optimal = sol_optimal.y[1]
            # Recalculate the wave force 
            forcing_function_optimal = create_forcing_function(t_eval, k_hydrostatic)
            
            # Call analysis function to find peak acceleration
            max_accel_t, max_accel_a = find_max_acceleration(
                t_eval, z_optimal, z_dot_optimal, opt_mass, opt_damping,
                k_hydrostatic, m_added, c_rad, k_drag, eta_pto
            )
            
            # Call the visualization function to create and show all plots
            plot_results_enhanced(t_eval, z_optimal, z_dot_optimal, forcing_function_optimal,
                                opt_mass, m_added, opt_damping, c_rad, k_drag,
                                max_accel_t, max_accel_a, buoy_diameter)
    else:
        # If optimization fails print failure message
        print("\nOptimization failed")
