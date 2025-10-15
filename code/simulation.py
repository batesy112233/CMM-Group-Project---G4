import numpy as np
from scipy.integrate import odeint

# --- SYSTEM CONSTANTS (A1's Research & Design Parameters) ---
# NOTE: A1 must replace these placeholder values with justified research values.
RHO = 1025.0       # kg/m^3 (Seawater Density)
G = 9.81           # m/s^2
A_WP = 5.0         # m^2 (Buoy Waterplane Area - used for K)
M_INF = 15000.0    # kg (Constant Added Mass - High frequency limit)
B_RAD_CONSTANT = 12000.0 # Ns/m (Radiation Damping - Crucial: research this!)

# --- OPTIMIZATION & SIMULATION SETTINGS (B1's Parameters) ---
T_SIMULATION = 200.0     # Total simulation time (s)
DT_STEP = 0.01           # Time step (s)
Y_MAX_LIMIT = 2.5        # Max displacement for survivability (m)

# Placeholder for A2's wave forcing function (must be defined elsewhere or imported)
def wave_forcing_function(t):
    # This must be replaced with A2's interpolation/regression code based on wave data.
    # For a placeholder, use a simple sine wave force:
    A_wave = 50000 # Amplitude (N)
    omega_wave = 0.5 # Rad/s
    return A_wave * np.sin(omega_wave * t)


# --- T1/T3: The ODE System Function (A1 & A3) ---
def ode_system_function(Y, t, m_buoy, c_pto):
    """
    Defines dY/dt for the ODE solver. Y = [displacement, velocity]
    """
    y, y_dot = Y
    
    # 1. Hydrostatic Stiffness (K) - Constant
    K = RHO * G * A_WP
    
    # 2. Total Inertial Mass (M_TOTAL) - Constant for a given m_buoy
    M_TOTAL = m_buoy + M_INF
    
    # 3. Total Damping Coefficient (C_TOTAL) - Varies with c_pto
    C_TOTAL = B_RAD_CONSTANT + c_pto
    
    # Get the external wave force (from A2)
    F_ex = wave_forcing_function(t) 
    
    # ODE 1: dy/dt = y_dot (Y[1])
    dy_dt = y_dot
    
    # ODE 2: d(y_dot)/dt = y_double_dot (the derived equation)
    y_double_dot = (F_ex - (C_TOTAL * y_dot) - (K * y)) / M_TOTAL
    
    return [dy_dt, y_double_dot]

# --- T3: Core Simulation Engine (A3) ---
def simulate_system(m_buoy, c_pto):
    """Runs the simulation and calculates instantaneous power."""
    
    time = np.arange(0, T_SIMULATION, DT_STEP)
    initial_conditions = [0.0, 0.0] # Start at equilibrium (y=0, y_dot=0)
    
    sol = odeint(
        func=ode_system_function, 
        y0=initial_conditions, 
        t=time, 
        args=(m_buoy, c_pto), # Parameters passed to the ODE function
    )
    
    displacement = sol[:, 0]
    velocity = sol[:, 1]
    
    # Calculate Instantaneous Power: P(t) = c_PTO * velocity^2
    power_inst = c_pto * (velocity**2) 
    
    return time, displacement, power_inst, velocity


# --- T4: Metrics and Optimization (B1) ---
def calculate_metrics(time, displacement, power_inst):
    """Calculates the P_avg and y_max for optimization."""
    
    # Discard the transient start-up phase (e.g., first 20% of data)
    t_discard = int(len(time) * 0.20)
    
    # 1. Average Power (P_avg)
    p_avg = np.mean(power_inst[t_discard:])
    
    # 2. Maximum Displacement (y_max)
    y_max = np.max(np.abs(displacement))
    
    return p_avg, y_max

def run_parameter_sweep():
    """Runs the grid search for optimal m_buoy and c_pto."""
    
    # Define ranges for grid search (B1 must tune these steps/limits)
    M_VALUES = np.arange(10000, 30000, 2000) # Example: 10 steps
    C_PTO_VALUES = np.arange(5000, 30000, 2000) # Example: 13 steps
    
    results_power = np.zeros((len(M_VALUES), len(C_PTO_VALUES)))
    
    best_power = 0.0
    optimal_params = None
    
    # Grid Search Loop
    for i, m in enumerate(M_VALUES):
        for j, c in enumerate(C_PTO_VALUES):
            
            # Run simulation
            time, disp, power_inst, _ = simulate_system(m_buoy=m, c_pto=c)
            
            # Calculate metrics
            p_avg, y_max = calculate_metrics(time, disp, power_inst)
            
            # Store result for heatmap visualization
            results_power[i, j] = p_avg
            
            # Check for optimality AND survivability constraint
            if p_avg > best_power and y_max <= Y_MAX_LIMIT:
                best_power = p_avg
                optimal_params = {'m': m, 'c_pto': c, 'power': p_avg, 'y_max': y_max}

    # B1 needs to add plotting/output code here
    print(f"Optimal Parameters Found: {optimal_params}")
    return optimal_params, results_power, M_VALUES, C_PTO_VALUES

if __name__ == '__main__':
    # This runs the optimization when the script is executed directly
    run_parameter_sweep()
