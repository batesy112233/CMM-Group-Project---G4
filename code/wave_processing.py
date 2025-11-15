import pandas as pd
import numpy as np
import config

""" Reads the wave data CSV, cleans it and resamples it to a new high-resolution time step """
def analyze_and_prepare_wave_data(dt_step=0.1):
    
    # Read the data from CSV file using pandas
    data = pd.read_csv('wave_elevation_data.csv', delimiter=',')
    time_coarse = data['Time_s'].to_numpy()
    wave_vertical_displacement_coarse = data['Probe1_Elevation_m'].to_numpy()

    # Data cleaning 
    valid_indices = ~np.isnan(wave_vertical_displacement_coarse) & ~np.isnan(time_coarse)
    time_coarse = time_coarse[valid_indices]
    wave_vertical_displacement_coarse = wave_vertical_displacement_coarse[valid_indices]
    
    # Store original data in config file
    config.WAVE_TIME_COARSE = time_coarse
    config.WAVE_VERTICAL_DISPLACEMENT_COARSE = wave_vertical_displacement_coarse

    # Resample data to high resolution 
    t_start, t_end = time_coarse[0], time_coarse[-1]
    num_points_hires = int(np.ceil((t_end - t_start) / dt_step)) + 1
    config.WAVE_TIME = np.linspace(t_start, t_end, num_points_hires)
    config.WAVE_VERTICAL_DISPLACEMENT = np.interp(config.WAVE_TIME, time_coarse, wave_vertical_displacement_coarse)
    
    # Print status message
    print(f"Loaded and resampled wave data to {len(config.WAVE_TIME)} points.") 

""" Calculates the wave excitation force at time 't' """
def create_forcing_function(t, k_hydro):
    
    # Uses the Froude-Krylov model to find the force at any instant
    wave_vertical_displacement_at_t = np.interp(t, config.WAVE_TIME, config.WAVE_VERTICAL_DISPLACEMENT, left=0, right=0)
    F_wave = k_hydro * wave_vertical_displacement_at_t
    return F_wave
