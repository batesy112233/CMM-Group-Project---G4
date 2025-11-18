"""
Wave data processing module
Handles loading, cleaning, and interpolating wave data

"""
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import config
import logging

logger = logging.getLogger(__name__)

""" Reads the wave data CSV, cleans it and resamples it to a new high-resolution time step """
def analyze_and_prepare_wave_data(file_path: str, dt_step: float = 0.1) -> bool:
    
    try:
        logger.info(f"Loading wave data from: {file_path}")
        data = pd.read_csv('wave_elevation_data.csv', delimiter=',')
        
        # Validate required columns
        if 'Time_s' not in data.columns or 'Probe1_Elevation_m' not in data.columns:
            logger.error("CSV must contain 'Time_s' and 'Probe1_Elevation_m' columns")
            return False
        
        time_coarse = data['Time_s'].to_numpy()
        wave_vertical_displacement_coarse = data['Probe1_Elevation_m'].to_numpy()
        
        # Remove NaN values
        valid_indices = ~np.isnan(wave_vertical_displacement_coarse) & ~np.isnan(time_coarse)
        time_coarse = time_coarse[valid_indices]
        wave_vertical_displacement_coarse = wave_vertical_displacement_coarse[valid_indices]
        
        if len(time_coarse) < 2:
            logger.error("Insufficient valid data points after removing NaN values")
            return False
        
        config.WAVE_TIME_COARSE = time_coarse
        config.WAVE_VERTICAL_DISPLACEMENT_COARSE = wave_vertical_displacement_coarse
        
        # Define time boundaries
        t_start, t_end = time_coarse[0], time_coarse[-1]
        
        # Create high-resolution time array
        num_points_hires = int(np.ceil((t_end - t_start) / dt_step)) + 1
        config.WAVE_TIME = np.linspace(t_start, t_end, num_points_hires)
        
        # Interpolate wave data using scipy for better performance
        config.wave_interp = interp1d(
            time_coarse, 
            wave_vertical_displacement_coarse,
            kind='linear',
            bounds_error=False,
            fill_value=0.0
        )
        config.WAVE_VERTICAL_DISPLACEMENT = config.wave_interp(config.WAVE_TIME)
        
        logger.info(f"Successfully loaded {len(time_coarse)} data points")
        logger.info(f"Resampled to {len(config.WAVE_TIME)} points at dt={dt_step}s")
        return True
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Error loading wave data: {type(e).__name__}: {str(e)}")
        return False

""" Calculates the wave forcing at time t """
def create_forcing_function(t: float, k_hydro: float) -> float:
    if config.wave_interp is None:
        return 0.0
    wave_displacement = config.wave_interp(t)
    return k_hydro * wave_displacement