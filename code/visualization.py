import numpy as np
import matplotlib.pyplot as plt
from config import *

""" Generates and saves a set of plots to visualize the results of the simulation """
def plot_results_enhanced(t_eval, z_optimal, z_dot_optimal, forcing_function, 
                         m_buoy, m_added, c_pto, c_rad, k_drag, 
                        max_accel_time=None, max_accel_value=None, buoy_diameter=8.0):

    print("\nGenerating plots...")
    
    # Recalculate Data for plotting
    wave_vertical_displacement_eval = np.interp(t_eval, WAVE_TIME, WAVE_VERTICAL_DISPLACEMENT, left=0, right=0)
    k_hydro = RHO_WATER * G * np.pi * (buoy_diameter / 2.0)**2
    
    # Recalculate all individual forces based on optimal solution
    F_wave = forcing_function
    F_hydrostatic = -k_hydro * z_optimal
    F_pto = -c_pto * z_dot_optimal
    
    # Check if radiation damping was enabled in simulation
    if RADIATION_DAMPING:
        F_radiation = -c_rad * z_dot_optimal
    else:
        F_radiation = np.zeros_like(z_dot_optimal)
    
    # Check if viscous drag was enabled in simulation
    if VISCOUS_DRAG:
        F_drag_calc = -k_drag * np.abs(z_dot_optimal) * z_dot_optimal
    else:
        F_drag_calc = np.zeros_like(z_dot_optimal)
        
    # Recalculate total force and acceleration to verify solver
    m_total = m_buoy + m_added
    F_total = F_wave + F_hydrostatic + F_pto + F_radiation + F_drag_calc
    z_double_dot = F_total / m_total

    # Configure the figure and subplots
    fig, axes = plt.subplots(9, 1, figsize=(14, 27), sharex=True)
    fig.suptitle('Buoy Optimization Results', fontsize=18, fontweight='bold')
    
    # Plot 0: Wave elevation
    axes[0].plot(WAVE_TIME_COARSE, WAVE_VERTICAL_DISPLACEMENT_COARSE, 'o', markersize=2, 
                    label='Original Data', color='c', alpha=0.7)
    axes[0].plot(t_eval, wave_vertical_displacement_eval, label='Interpolated', 
                    color='b', linestyle='-', linewidth=1.5)
    axes[0].set_title('Wave Elevation Data', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Elevation (m)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 1: Wave forcing
    axes[1].plot(t_eval, F_wave/1000, label='Wave Forcing', color='blue', linewidth=1.5)
    axes[1].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[1].set_title('1. Wave Forcing', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Force (kN)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Plot 2: Hydrostatic Force
    axes[2].plot(t_eval, F_hydrostatic/1000, label='Hydrostatic Restoring', 
                    color='green', linewidth=1.5)
    axes[2].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[2].set_title('2. Hydrostatic Restoring Force', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Force (kN)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    # Plot 3: PTO Force
    axes[3].plot(t_eval, F_pto/1000, label='PTO Damping', 
                    color='red', linewidth=1.5)
    axes[3].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[3].axhline(MAX_PTO_FORCE/1000, color='red', linestyle=':', alpha=0.5, linewidth=2, label='Max PTO Force')
    axes[3].axhline(-MAX_PTO_FORCE/1000, color='red', linestyle=':', alpha=0.5, linewidth=2)
    axes[3].set_title('3. PTO Damping Force', fontsize=12, fontweight='bold')
    axes[3].set_ylabel('Force (kN)')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)
    
    # Plot 4: Radiation Damping
    if RADIATION_DAMPING:
        axes[4].plot(t_eval, F_radiation/1000, label='Radiation Damping', 
                        color='purple', linewidth=1.5)
        axes[4].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
        axes[4].set_title('4. Radiation Damping Force', fontsize=12, fontweight='bold')
        axes[4].set_ylabel('Force (kN)')
        axes[4].legend()
        axes[4].grid(True, alpha=0.3)
    else:
        # If disabled just put text on plot
        axes[4].text(0.5, 0.5, 'Radiation Damping: DISABLED', 
                        ha='center', va='center', transform=axes[4].transAxes, fontsize=12)
        axes[4].set_title('4. Radiation Damping Force (DISABLED)', fontsize=12, fontweight='bold')
        axes[4].set_ylabel('Force (kN)')
        axes[4].grid(True, alpha=0.3)
    
    # Plot 5: Viscous Drag 
    if VISCOUS_DRAG:
        axes[5].plot(t_eval, F_drag_calc/1000, label='Viscous Drag', 
                        color='orange', linewidth=1.5)
        axes[5].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
        axes[5].set_title('5. Viscous Drag Force', fontsize=12, fontweight='bold')
        axes[5].set_ylabel('Force (kN)')
        axes[5].legend()
        axes[5].grid(True, alpha=0.3)
    else:
        # If disabled just put text on plot
        axes[5].text(0.5, 0.5, 'Viscous Drag: DISABLED', 
                        ha='center', va='center', transform=axes[5].transAxes, fontsize=12)
        axes[5].set_title('5. Viscous Drag Force (DISABLED)', fontsize=12, fontweight='bold')
        axes[5].set_ylabel('Force (kN)')
        axes[5].grid(True, alpha=0.3)
    
    # PLot 6: Acceleration
    axes[6].plot(t_eval, z_double_dot, label='Acceleration', color='darkorange', linewidth=1.5)
    axes[6].set_title('6. Buoy Acceleration', fontsize=12, fontweight='bold')
    axes[6].set_ylabel('Accel. ($m/s^2$)', color='darkorange')
    axes[6].axhline(0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
    axes[6].axhline(G, color='grey', linestyle=':', alpha=0.5, label='1G')
    axes[6].axhline(-G, color='grey', linestyle=':', alpha=0.5)

    # If max acceleration isn't found plot a marker
    if max_accel_time is not None:
        axes[6].plot(max_accel_time, max_accel_value, 'ro', markersize=5, label='Max Abs Accel')
        axes[6].text(max_accel_time, max_accel_value * 1.05, 
                    f'Max: {max_accel_value:.1f} m/s²',
                    fontsize=9, ha='center', color='red')
    axes[6].legend(loc='best')
    axes[6].grid(True, alpha=0.3)

    # Plot 7: Position and Velocity on a twin axis
    ax8_twin = axes[7].twinx()
    axes[7].plot(t_eval, z_optimal, label='Position', color='r', linewidth=1.5)
    ax8_twin.plot(t_eval, z_dot_optimal, label='Velocity', 
                    color='purple', linestyle='--', linewidth=1.5)
    
    axes[7].set_title(f'7. Buoy Response (m_total = {m_buoy+m_added:.0f} kg)', 
                        fontsize=12, fontweight='bold')
    axes[7].set_ylabel('Position (m)', color='r')
    ax8_twin.set_ylabel('Velocity (m/s)', color='purple')
    
    axes[7].axhline(MAX_DISPLACEMENT, color='r', linestyle=':', alpha=0.5, linewidth=2, label='Max Disp.')
    axes[7].axhline(-MAX_DISPLACEMENT, color='r', linestyle=':', alpha=0.5, linewidth=2)

    lines, labels = axes[7].get_legend_handles_labels()
    lines2, labels2 = ax8_twin.get_legend_handles_labels()
    axes[7].legend(lines + lines2, labels + labels2, loc='best')
    axes[7].grid(True, alpha=0.3)
    
    # Plot 8: Power 
    instant_power = c_pto * (z_dot_optimal**2) / 1000
    axes[8].plot(t_eval, instant_power, label='Instantaneous Power', color='green', linewidth=1)
    axes[8].axhline(np.mean(instant_power[t_eval > 50]), 
                        color='darkgreen', linestyle='--', linewidth=2,
                        label=f'Average Power = {np.mean(instant_power[t_eval > 50]):.1f} kW')
    axes[8].fill_between(t_eval, 0, instant_power, alpha=0.3, color='green')
    axes[8].set_title('8. Power Generation', fontsize=12, fontweight='bold')
    axes[8].set_xlabel('Time (s)', fontsize=11)
    axes[8].set_ylabel('Power (kW)')
    axes[8].legend()
    axes[8].grid(True, alpha=0.3)
    axes[8].set_ylim(bottom=0)

    # Finalise and save plots
    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    plt.savefig('buoy_results.png', dpi=150, bbox_inches='tight')
    print("Plot saved as 'buoy_results.png'")
    plt.show()
