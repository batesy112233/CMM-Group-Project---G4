import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt # --- NEW: Import matplotlib for plotting ---

# --- SYSTEM CONSTANTS (A1's Research & Design Parameters) ---
RHO = 1025.0 	 	# kg/m^3 (Seawater Density)
G = 9.81 	 	    # m/s^2
A_WP = 5.0 	 	    # m^2 (Buoy Waterplane Area - used for K)
M_INF = 15000.0 	# kg (Constant Added Mass)
B_RAD_CONSTANT = 12000.0 # Ns/m (Radiation Damping)

# --- WAVE FORCING PARAMETERS (A2's Data Set) ---
F_WAVE_AMPLITUDE = 50000.0 # N (Amplitude of the sinusoidal wave excitation force, F_amp)
OMEGA_WAVE = 0.5 	# Rad/s (Frequency of the sinusoidal wave excitation, Omega)

# --- OPTIMIZATION & SIMULATION SETTINGS (B1's Parameters) ---
T_SIMULATION = 200.0 	# Total simulation time (s)
DT_STEP = 0.01 	 	# Time step (s)
Y_MAX_LIMIT = 2.5 	# Max displacement for survivability (m)

# --- T2: Wave Forcing Function (Monochromatic Wave) ---
def wave_forcing_function(t):
	"""
	Generates the sinusoidal excitation force, F_ex(t), 
    consistent with the analytical SDOF approach.
	Note: Using cosine for consistency with the image provided.
	"""
	return F_WAVE_AMPLITUDE * np.cos(OMEGA_WAVE * t)


# --- T1/T3: The Numerical ODE System Function (A1 & A3) ---
def ode_system_function(Y, t, m_buoy, c_pto):
	"""
	Defines dY/dt for the numerical ODE solver. Y = [displacement, velocity]
	The equation of motion is: M_TOTAL*y_ddot + C_TOTAL*y_dot + K*y = F_ex
	"""
	y, y_dot = Y
	
	# 1. Hydrostatic Stiffness (K)
	K = RHO * G * A_WP
	
	# 2. Total Inertial Mass (M_TOTAL)
	M_TOTAL = m_buoy + M_INF
	
	# 3. Total Damping Coefficient (C_TOTAL)
	C_TOTAL = B_RAD_CONSTANT + c_pto
	
	# Get the external wave force
	F_ex = wave_forcing_function(t)	
	
	dy_dt = y_dot
	
	# ODE 2: d(y_dot)/dt = y_double_dot (Acceleration)
	y_double_dot = (F_ex - (C_TOTAL * y_dot) - (K * y)) / M_TOTAL
	
	return [dy_dt, y_double_dot]

# --- T3: Core Simulation Engine (A3) ---
def simulate_system(m_buoy, c_pto):
	"""Runs the numerical simulation and calculates instantaneous power."""
	
	# --- NUMERICAL SOLUTION ---
	time = np.arange(0, T_SIMULATION, DT_STEP)
	initial_conditions = [0.0, 0.0] # Start at equilibrium
	
	sol = odeint(
		func=ode_system_function,	
		y0=initial_conditions,	
		t=time,	
		args=(m_buoy, c_pto), # Parameters passed to the ODE function
	)
	
	displacement = sol[:, 0]
	velocity = sol[:, 1]
	power_inst = c_pto * (velocity**2)	
	
	# --- ANALYTICAL STEADY-STATE SOLUTION CALCULATION ---
	
	# 1. System Properties
	K = RHO * G * A_WP
	M_TOTAL = m_buoy + M_INF
	C_TOTAL = B_RAD_CONSTANT + c_pto
	
	# 2. Characteristic Frequencies and Ratios
	omega_0 = np.sqrt(K / M_TOTAL) # Natural Frequency (omega_0)
	zeta = C_TOTAL / (2 * np.sqrt(M_TOTAL * K)) # Damping Ratio (delta or zeta)
	r = OMEGA_WAVE / omega_0 # Frequency Ratio (r = Omega / omega_0)
	
	# 3. Static Deflection (x_0)
	x_0 = F_WAVE_AMPLITUDE / K 
	
	# 4. Magnification Factor (Mu) - X/x_0
	denominator_sq = (1 - r**2)**2 + (2 * zeta * r)**2
	Mu = 1 / np.sqrt(denominator_sq)
	
	# 5. Steady-State Amplitude (X) and Phase (phi)
	analytical_amplitude_X = Mu * x_0
	analytical_phase_phi = -np.arctan2(2 * zeta * r, 1 - r**2) # tan(phi) = -2*delta*r / (1-r^2)
	
	analytical_power_avg = calculate_analytical_power(analytical_amplitude_X, c_pto, OMEGA_WAVE)

	return time, displacement, power_inst, velocity, analytical_amplitude_X, analytical_power_avg


# --- Analytical Power Calculation ---
def calculate_analytical_power(amplitude_X, c_pto, omega):
	"""
	Calculates the average power P_avg for the analytical steady-state solution.
	The velocity is v(t) = -X * omega * sin(omega*t + phi).
	Power is P(t) = c_pto * v(t)^2.
	P_avg = (1/T) * integral(P(t) dt) = 0.5 * c_pto * (X * omega)^2
	"""
	V_amplitude = amplitude_X * omega
	P_avg = 0.5 * c_pto * (V_amplitude**2)
	return P_avg


# --- T4: Metrics and Optimization (B1) ---
def calculate_metrics(time, displacement, power_inst):
	"""Calculates the P_avg and y_max for optimization."""
	
	# Discard the transient start-up phase (e.g., first 20% of data)
	t_discard = int(len(time) * 0.20)
	
	# 1. Average Power (P_avg) from Numerical Simulation
	p_avg_numerical = np.mean(power_inst[t_discard:])
	
	# 2. Maximum Displacement (y_max) from Numerical Simulation
	y_max = np.max(np.abs(displacement))
	
	return p_avg_numerical, y_max

# --- NEW: Plotting Function ---
def plot_results(time, displacement, wave_force, optimal_params):
    """Generates two subplots: Wave Force and Buoy Displacement."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f"WEC Response for Optimal Parameters: m={optimal_params['m']:.0f}kg, c_pto={optimal_params['c_pto']:.0f}Ns/m")

    # Plot 1: Wave Excitation Force (The Input/Wave Action)
    ax1.plot(time, wave_force / 1000.0, label='Wave Excitation Force', color='blue')
    ax1.set_title('1. Wave Excitation Force (Input Action)')
    ax1.set_ylabel('Force (kN)')
    ax1.grid(True)
    ax1.set_xlim([0, T_SIMULATION])
    
    # Plot 2: Buoy Displacement (The Output Response)
    ax2.plot(time, displacement, label='Buoy Displacement', color='red')
    ax2.axhline(Y_MAX_LIMIT, color='k', linestyle='--', linewidth=1, label=f'Max Limit ({Y_MAX_LIMIT}m)')
    ax2.axhline(-Y_MAX_LIMIT, color='k', linestyle='--', linewidth=1)
    ax2.set_title('2. Buoy Displacement (Output Response)')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Displacement (m)')
    ax2.legend()
    ax2.grid(True)
    
    # Show only the steady-state for better detail (e.g., last 50s)
    ax2.set_xlim([T_SIMULATION - 50, T_SIMULATION])
    ax1.set_xlim([T_SIMULATION - 50, T_SIMULATION])

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

def run_parameter_sweep():
	"""Runs the grid search for optimal m_buoy and c_pto."""
	
	# Define ranges for grid search (B1 must tune these steps/limits)
	M_VALUES = np.arange(10000, 30000, 2000) # Example: 10 steps
	C_PTO_VALUES = np.arange(5000, 30000, 2000) # Example: 13 steps
	
	results_power_numerical = np.zeros((len(M_VALUES), len(C_PTO_VALUES)))
	results_power_analytical = np.zeros((len(M_VALUES), len(C_PTO_VALUES))) # Store analytical results
	
	best_power = 0.0
	optimal_params = None
	
	# Grid Search Loop
	for i, m in enumerate(M_VALUES):
		for j, c in enumerate(C_PTO_VALUES):
			
			# Run simulation and analytical calculation
			time, disp, power_inst, _, analytical_amp, p_avg_analytical = simulate_system(m_buoy=m, c_pto=c)
			
			# Calculate numerical metrics
			p_avg_numerical, y_max = calculate_metrics(time, disp, power_inst)
			
			# Store results
			results_power_numerical[i, j] = p_avg_numerical
			results_power_analytical[i, j] = p_avg_analytical
			
			# Check for optimality (using NUMERICAL result, as it includes the transient)
			if p_avg_numerical > best_power and y_max <= Y_MAX_LIMIT:
				best_power = p_avg_numerical
				optimal_params = {
					'm': m, 
					'c_pto': c, 
					'power_num': p_avg_numerical, 
					'power_anl': p_avg_analytical,
					'y_max': y_max,
					'y_steady_state_anl': analytical_amp
				}

	print("--- Optimization Results ---")
	if optimal_params:
		print(f"Optimal Parameters Found (Numerical Power): {optimal_params}")
		print(f"\nExample comparison for optimal point:")
		print(f"Numerical P_avg: {optimal_params['power_num']:.2f} W")
		print(f"Analytical P_avg: {optimal_params['power_anl']:.2f} W")
		print(f"Difference: {abs(optimal_params['power_num'] - optimal_params['power_anl']):.2f} W")

		# --- NEW: Re-run optimal simulation for plotting data ---
		time, disp, _, vel, _, _ = simulate_system(
			m_buoy=optimal_params['m'], 
			c_pto=optimal_params['c_pto']
		)
		
		# Generate the wave force time series for plotting
		wave_force_data = wave_forcing_function(time)

		# Call the plotting function
		plot_results(time, disp, wave_force_data, optimal_params)

	else:
		print("No optimal parameters found within the survivability limit.")
	
	return optimal_params, results_power_numerical, M_VALUES, C_PTO_VALUES

if __name__ == '__main__':
	run_parameter_sweep()
