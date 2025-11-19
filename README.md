<div align="center">
  <img 
    src="https://cdn.offshorewind.biz/wp-content/uploads/sites/6/2018/08/02153924/american-wave-powered-buoy-reaches-the-adriatic.jpg" 
    alt="PAWEC Project Banner"
    width="1000"
    height="600"
    style="border-radius: 10px;"
  />
  <p><em>Numerical Modelling and Optimization for Point Absorber Wave Energy Converters</em></p>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)

## Project Overview

This system models a floating buoy that generates power through vertical oscillation in the North Sea. This repository contains the source code for this model and numerical modelling, focused on the optimization of a Point Absorber Wave Energy Converter (PAWEC).

The objective of this software is to maximize the average power capture from irregular North Sea wave conditions while maintaining structural integrity. 

The optimization strategy involves tuning two design parameters: the Buoy's Mass and the Power Take-Off (PTO) Damping Coefficient. By utilizing a time-domain simulation, the model accounts for hydrodynamic constraints for energy capture.

## Table of Contents

- [Installation and Setup](#installation-and-setup)
- [Numerical Methods & Implementation](#numerical-methods--implementation)
- [Repository Structure](#repository-structure)

<br>

## Installation and Setup

### Installation

1. Go to the project's GitHub page.
2. Click ***Code → Download ZIP***.
3. Extract the ZIP file to a folder of your choice on your computer.

**OR**  

1. Open your terminal or command prompt.
2. Navigate to the directory where you want to store the project.
3. Execute the git clone command:
```bash
git clone https://github.com/batesy11233/CMM-Group-Project---G4.git
cd CMM-Group-Project---G4
```
### Dependencies
Use an IDE ___ie. Spyder(reccomended)___ to run the code.  
Before running, make sure these Python libraries are installed on your system:

* NumPy
* SciPy
* Matplotlib
* Pandas

If any are missing, you can download then using your chosen IDE's package manager or terminal by running this:

```bash
pip install numpy scipy matplotlib pandas 
```
If you're using VS Code, Anaconda or Spyder, these are likely already installed.
### Running the model
 
* Open the project in your IDE
* Run the file **`main.py`** using your IDE's run command

**OR**  
* If using the terminal, ensure you are in the project's root directory (CMM-Group-Project---G4)
* Excecute the main file

```bash
python main.py
```

### Expected Result
* Excecuting `main.py` should:

  * Loads wave elevation data
  * Runs time-domain simulation & optimization
  * Checks acceleration limits
  * Outputs figures to `buoy_results.png`
<br>

## Numerical Methods & Implementation

This project employs the following numerical methods to handle the irregular nature of ocean waves and solve the hydrodynamic equations governing buoy motion.

| Algorithm | Methodology | Application | Implementation File |
| :--- | :--- | :--- | :--- |
| **ODE Solver** | Runge-Kutta 45 (RK45) with adaptive step-size | Solves 2nd-order equation of motion for buoy dynamics with variable time steps | `simulation.py` |
| **Interpolation** | Linear interpolation (scipy.interp1d) | Creates high-resolution wave elevation from coarse measurements for smooth forcing | `wave_processing.py` |
| **Root Finding** | Brent's Method (scipy.optimize.brentq) | Finds jerk function roots to locate acceleration extrema for structural validation | `analysis.py` |
| **Spline Interpolation** | Cubic Spline (scipy.CubicSpline) | Creates continuous acceleration function from discrete ODE solutions for derivative analysis | `analysis.py` |

### ODE Solver Details:
- **Method**: Runge-Kutta 45 (RK45) with adaptive step-size control
- **Implementation**: `run_simulation()` function in `simulation.py` using `scipy.integrate.solve_ivp(method='RK45')`
- **Features**: Maximum step size enforcement (0.5s), dense output for continuous solution evaluation
- **Equation Solved**: $(m_{\text{buoy}} + m_{\text{added}})\ddot{z} = F_{\text{wave}} + F_{\text{hydrostatic}} + F_{\text{PTO}} + F_{\text{radiation}} + F_{\text{drag}}$

### Interpolation Methods Details:
- **Linear Interpolation**: Creates high-resolution wave elevation data from coarse measurements for continuous forcing function
- **Implementation**: `analyze_and_prepare_wave_data()` function in `wave_processing.py` using `scipy.interpolate.interp1d(kind='linear')`
- **Cubic Spline**: Generates smooth acceleration functions from discrete ODE solutions for analytical differentiation
- **Implementation**: `find_max_acceleration()` function in `analysis.py` using `scipy.interpolate.CubicSpline()`

### Root Finding Details:
- **Method**: Brent's method (brentq) combining bisection, secant, and inverse quadratic interpolation
- **Implementation**: `find_max_acceleration()` function in `analysis.py` using `scipy.optimize.brentq()`
- **Application**: Finds roots of jerk function $(\dddot{z} = 0)$ to identify acceleration extrema for structural constraint validation
- **Process**: Uses cubic spline derivative to create jerk function, then locates roots where acceleration is maximized

## Repository Structure

The following table shows what each python file does.

### Core Simulation & Physics

| File | Purpose |
| :--- | :--- |
| **`physics.py`** | Calculates hydrodynamic coefficients: added mass, radiation damping, viscous drag, hydrostatic stiffness, and creates buoy properties object |
| **`simulation.py`** | ODE solver wrapper using RK45 method: sets up time span, initial conditions, and handles simulation execution with error management |
| **`dynamics.py`** | Implements buoy equation of motion with wave forcing, hydrostatic, PTO, radiation, and drag forces |
| **`config.py`** | Central configuration with physical constants, optimization bounds, buoy properties dataclass, and simulation switches|

### Processing, Analysis & Visualization

| File | Purpose |
| :--- | :--- |
| **`wave_processing.py`** | Loads and preprocesses wave data: reads CSV files, removes NaN values, performs linear interpolation, and creates wave forcing function |
| **`analysis.py`** | Acceleration analysis using cubic splines and Brent's method to find peak acceleration for structural constraint validation |
| **`visualization.py`** | Generates comprehensive 9-panel results visualization: wave data, all force components, acceleration, buoy response, and power generation |
| **`wave_plotter.py`** | Processes raw .DAT wave probe files: reads binary data, generates individual/combined plots, converts to CSV format for analysis |
| **`single_velocity.py`** | Wave velocity analysis: reads probe data, calculates instantaneous velocity using gradient, computes mean/RMS statistics, and generates validation plots |

### Entry Points & Optimization

| File | Purpose |
| :--- | :--- |
| **`main.py`** | Orchestrates complete optimization pipeline: loads wave data, creates buoy properties, runs differential evolution optimization, and generates final results |
| **`optimization.py`** | Function for optimization: evaluates mass/damping parameters, checks constraints, calculates electrical power with PTO efficiency |
| **`param_scan.py`** | Parameter sweep analysis: systematically tests mass/damping combinations, filters invalid cases, and generates power vs mass curves for sensitivity analysis |

### Data Files
| File | Purpose |
| :--- | :--- |
| **`wave_elevation_data.csv`** | Contains a set of raw, real North Sea wave elevation measurements |
| **`buoy_results.png`** | Visualization of optimization results including wave elevation, forcing functions, hydrodynamic forces, buoy response, and power generation |
<br>
