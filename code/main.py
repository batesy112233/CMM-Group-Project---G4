"""
Main module.
Performs the optimization and simulation process.

"""
import numpy as np
from scipy.optimize import minimize, differential_evolution
import sys
import logging

# Import all functions and variables from other files
import config
from wave_processing import analyze_and_prepare_wave_data, create_forcing_function
from physics import create_buoy_properties
from simulation import run_simulation
from optimization import objective_function
from analysis import find_max_acceleration
from visualization import plot_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    
    # Initialize and load data
    logger.info("="*60)
    logger.info("WAVE ENERGY BUOY OPTIMIZATION")
    logger.info("="*60)
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "wave_data_final.csv"
        logger.info(f"No file path provided, using default: {file_path}")
    
    # Call function to read, clean and resample the wave data
    if not analyze_and_prepare_wave_data(file_path, dt_step=0.1):
        logger.error("Failed to load wave data. Exiting.")
        sys.exit(1)
    
    # Create buoy properties
    buoy_props = create_buoy_properties(diameter=8.0, height=6.0, eta_pto=0.90)
    
    logger.info(f"\nBuoy Properties:")
    logger.info(f"  Diameter: {buoy_props.diameter} m")
    logger.info(f"  Draft: {buoy_props.height} m")
    logger.info(f"  Waterplane Area: {buoy_props.area:.2f} m²")
    logger.info(f"  Hydrostatic stiffness: {buoy_props.k_hydrostatic:.0f} N/m")
    logger.info(f"  Added mass: {buoy_props.m_added:.0f} kg")
    logger.info(f"  Radiation damping: {buoy_props.c_rad:.0f} Ns/m")
    logger.info(f"  Drag coefficient: {buoy_props.k_drag:.2f} kg/m")
    logger.info(f"  PTO efficiency: {buoy_props.eta_pto*100:.0f}%")
    
    # Optimize
    x0 = [np.mean(config.MASS_BOUNDS), np.mean(config.DAMPING_BOUNDS)]
    bounds = [config.MASS_BOUNDS, config.DAMPING_BOUNDS]
    
    logger.info(f"\nStarting optimization (Differential Evolution)...")
    logger.info(f"Initial guess: m={x0[0]:.0f} kg, c={x0[1]:.0f} Ns/m")
    
    result = differential_evolution(
        objective_function,
        bounds,
        args=(buoy_props,),
        strategy='best1bin', # The standard strategy
        maxiter=10,          # Generations (lower this if it takes too long)
        popsize=5,          # Population size (higher = more searching, slower)
        tol=0.1,            # Tolerance for convergence
        disp=True            # Print progress
    )
    
    if result.success:
        logger.info("\n" + "="*60)
        logger.info("OPTIMIZATION SUCCESSFUL")
        logger.info("="*60)
        
        opt_mass, opt_damping = result.x
        max_power_electrical = -result.fun
        
        logger.info(f"\nOptimal Parameters:")
        logger.info(f"  Buoy Mass: {opt_mass:.0f} kg")
        logger.info(f"  Total Mass: {opt_mass + buoy_props.m_added:.0f} kg")
        logger.info(f"  PTO Damping: {opt_damping:.0f} Ns/m")
        logger.info(f"  Electrical Power: {max_power_electrical/1000.0:.2f} kW")
        logger.info(f"  Annual Energy: ~{max_power_electrical * 8.76:.0f} MWh/year")
        
        # Run final simulation
        logger.info("\nRunning final simulation...")
        
        sol = run_simulation(opt_mass, opt_damping, buoy_props)
        
        if sol.success:
            # Evaluate solution for plotting
            t_eval = np.linspace(config.WAVE_TIME[0], config.WAVE_TIME[-1], config.EVAL_POINTS)
            z_optimal = sol.sol(t_eval)[0]
            z_dot_optimal = sol.sol(t_eval)[1]
            forcing = np.array([create_forcing_function(t, buoy_props.k_hydrostatic) for t in t_eval])
            
            max_accel_t, max_accel_a = find_max_acceleration(
                t_eval, z_optimal, z_dot_optimal, opt_mass, opt_damping, buoy_props
            )
            
            plot_results(t_eval, z_optimal, z_dot_optimal, forcing, opt_mass, 
                        buoy_props, opt_damping, max_accel_t, max_accel_a)
        else:
            logger.error("Final simulation failed")
    else:
        logger.error("Optimization failed")
        logger.error(result.message)

if __name__ == "__main__":
    main()
