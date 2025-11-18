"""
Visualization module.
Generates and saves plots of the results.

"""
import numpy as np
import matplotlib.pyplot as plt
import logging
from typing import Optional
import config
from config import BuoyProperties

logger = logging.getLogger(__name__)

""" Generates and saves a set of plots to visualize the results of the simulation """
def plot_results(t_eval: np.ndarray, z_optimal: np.ndarray, z_dot_optimal: np.ndarray,
                forcing_function: np.ndarray, m_buoy: float, buoy_props: BuoyProperties,
                c_pto: float, max_accel_time: Optional[float] = None, 
                max_accel_value: Optional[float] = None):
    
    logger.info("Generating plots...")
    
    wave_displacement_eval = config.wave_interp(t_eval)
    
    # Calculate forces
    F_wave = forcing_function
    F_hydrostatic = -buoy_props.k_hydrostatic * z_optimal
    F_pto = -c_pto * z_dot_optimal
    F_radiation = -buoy_props.c_rad * z_dot_optimal if config.RADIATION_DAMPING else np.zeros_like(z_dot_optimal)
    F_drag = -buoy_props.k_drag * np.abs(z_dot_optimal) * z_dot_optimal if config.VISCOUS_DRAG else np.zeros_like(z_dot_optimal)
    
    # Calculate acceleration
    m_total = m_buoy + buoy_props.m_added
    F_total = F_wave + F_hydrostatic + F_pto + F_radiation + F_drag
    z_double_dot = F_total / m_total
    
    # Create figure with 9 plots
    fig, axes = plt.subplots(9, 1, figsize=(14, 27), sharex=True)
    fig.suptitle('Wave Energy Buoy Optimization Results', fontsize=18, fontweight='bold')
    
    # Plot 1: Wave Data
    axes[0].plot(config.WAVE_TIME_COARSE, config.WAVE_VERTICAL_DISPLACEMENT_COARSE, 'o', 
                markersize=2, label='Original', color='c', alpha=0.7)
    axes[0].plot(t_eval, wave_displacement_eval, label='Interpolated', 
                color='b', linewidth=1.5)
    axes[0].set_title('Wave Elevation Data')
    axes[0].set_ylabel('Elevation (m)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Wave Forcing
    axes[1].plot(t_eval, F_wave/1000, color='blue', linewidth=1.5)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[1].set_title('Wave Forcing')
    axes[1].set_ylabel('Force (kN)')
    axes[1].grid(True, alpha=0.3)
    
    # Plot 3: Hydrostatic Force
    axes[2].plot(t_eval, F_hydrostatic/1000, color='green', linewidth=1.5)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[2].set_title('Hydrostatic Restoring Force')
    axes[2].set_ylabel('Force (kN)')
    axes[2].grid(True, alpha=0.3)
    
    # Plot 4: PTO Force
    axes[3].plot(t_eval, F_pto/1000, color='red', linewidth=1.5)
    axes[3].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[3].axhline(config.MAX_PTO_FORCE/1000, color='red', linestyle=':', alpha=0.5, linewidth=2)
    axes[3].axhline(-config.MAX_PTO_FORCE/1000, color='red', linestyle=':', alpha=0.5, linewidth=2)
    axes[3].set_title('PTO Damping Force')
    axes[3].set_ylabel('Force (kN)')
    axes[3].grid(True, alpha=0.3)
    
    # Plot 5: Radiation Damping
    axes[4].plot(t_eval, F_radiation/1000, color='purple', linewidth=1.5)
    axes[4].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[4].set_title(f'Radiation Damping ({"ENABLED" if config.RADIATION_DAMPING else "DISABLED"})')
    axes[4].set_ylabel('Force (kN)')
    axes[4].grid(True, alpha=0.3)
    
    # Plot 6: Viscous Drag
    axes[5].plot(t_eval, F_drag/1000, color='orange', linewidth=1.5)
    axes[5].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[5].set_title(f'Viscous Drag ({"ENABLED" if config.VISCOUS_DRAG else "DISABLED"})')
    axes[5].set_ylabel('Force (kN)')
    axes[5].grid(True, alpha=0.3)
    
    # Plot 7: Acceleration
    axes[6].plot(t_eval, z_double_dot, color='darkorange', linewidth=1.5)
    axes[6].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[6].axhline(config.G, color='grey', linestyle=':', alpha=0.5)
    axes[6].axhline(-config.G, color='grey', linestyle=':', alpha=0.5)
    if max_accel_time is not None:
        axes[6].plot(max_accel_time, max_accel_value, 'ro', markersize=5)
        axes[6].text(max_accel_time, max_accel_value*1.05, 
                    f'{max_accel_value:.1f} m/s²', fontsize=9, ha='center', color='red')
    axes[6].set_title('Buoy Acceleration')
    axes[6].set_ylabel('Accel (m/s²)')
    axes[6].grid(True, alpha=0.3)
    
    # Plot 8: Position & Velocity
    ax8_twin = axes[7].twinx()
    axes[7].plot(t_eval, z_optimal, color='r', linewidth=1.5, label='Position')
    ax8_twin.plot(t_eval, z_dot_optimal, color='purple', linestyle='--', linewidth=1.5, label='Velocity')
    axes[7].axhline(config.MAX_DISPLACEMENT, color='r', linestyle=':', alpha=0.5, linewidth=2)
    axes[7].axhline(-config.MAX_DISPLACEMENT, color='r', linestyle=':', alpha=0.5, linewidth=2)
    axes[7].set_title(f'Buoy Response (m_total = {m_buoy + buoy_props.m_added:.0f} kg)')
    axes[7].set_ylabel('Position (m)', color='r')
    ax8_twin.set_ylabel('Velocity (m/s)', color='purple')
    axes[7].grid(True, alpha=0.3)
    
    # Plot 9: Power
    instant_power = c_pto * (z_dot_optimal**2) / 1000
    axes[8].plot(t_eval, instant_power, color='green', linewidth=1)
    axes[8].axhline(np.mean(instant_power[t_eval > config.STEADY_STATE_CUTOFF]), 
                   color='darkgreen', linestyle='--', linewidth=2,
                   label=f'Avg = {np.mean(instant_power[t_eval > config.STEADY_STATE_CUTOFF]):.1f} kW')
    axes[8].fill_between(t_eval, 0, instant_power, alpha=0.3, color='green')
    axes[8].set_title('Power Generation')
    axes[8].set_xlabel('Time (s)')
    axes[8].set_ylabel('Power (kW)')
    axes[8].legend()
    axes[8].grid(True, alpha=0.3)
    axes[8].set_ylim(bottom=0)
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    plt.savefig('buoy_results.png', dpi=150, bbox_inches='tight')
    logger.info("Plot saved as 'buoy_results.png'")
    plt.show()
