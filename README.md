<div align="center">
  <img 
    src="https://cdn.offshorewind.biz/wp-content/uploads/sites/6/2018/08/02153924/american-wave-powered-buoy-reaches-the-adriatic.jpg" 
    alt="PAWEC Project Banner"
    width="800"
  />
  <p><em>Numerical Modelling and Optimization for Point Absorber Wave Energy Converters</em></p>
</div>
[![Python](https://img.shields.io/badge/python-3%2B-blue.svg)](https://www.python.org/)
[![Method](https://img.shields.io/badge/solver-RK45-orange.svg)]()
[![Documentation](https://img.shields.io/badge/docs-pdf-lightgrey.svg)](CMM3_Group_Project.pdf)

</div>

## Project Overview

 This system models a floating buoy that generates power through vertical oscillation in the North Sea. This repository contains the source code for this model and numerical modelling, focused on the optimization of a Point Absorber Wave Energy Converter (PAWEC).

The objective of this software is to maximize the average power capture from irregular North Sea wave conditions while maintaining structural integrity. 

The optimization strategy involves tuning two design parameters: the Buoy's Mass and the Power Take-Off (PTO) Damping Coefficient. By utilizing a time-domain simulation, the model accounts for hydrodynamic constraints for energy capture.

## Table of Contents

- [Installation and Setup](#installation-and-setup)
- [Numerical Methods & Implementation](#numerical-methods--implementation)
- [Repository Structure](#repository-structure)

## Installation and Setup

### Installation

Clone the repository:

```bash
git clone [https://github.com/batesy112233/CMM-Group-Project.git](https://github.com/batesy112233/CMM-Group-Project.git)
```


### Dependencies

The project requires the standard scientific Python stack that can be installed using pip:

* NumPy
* SciPy
* Matplotlib

```bash
pip install numpy scipy matplotlib pandas
```

<br>

## Numerical Methods & Implementation

This project employs sophisticated numerical methods to handle the irregular nature of ocean waves and solve the complex hydrodynamic equations governing buoy motion.

| Algorithm | Methodology | Application | Implementation File |
| :--- | :--- | :--- | :--- |
| **ODE Solver** | Runge-Kutta 45 (RK45) with adaptive step-size | Solves 2nd-order equation of motion for buoy dynamics with variable time steps | `simulation.py` |
| **Interpolation** | Linear interpolation (scipy.interp1d) | Creates high-resolution wave elevation from coarse measurements for smooth forcing | `wave_processing.py` |
| **Root Finding** | Brent's Method (scipy.optimize.brentq) | Finds jerk function roots to locate acceleration extrema for structural validation | `analysis.py` |
| **Spline Interpolation** | Cubic Spline (scipy.CubicSpline) | Creates continuous acceleration function from discrete ODE solutions for derivative analysis | `analysis.py` |

### ODE Solver Details:
- **Method**: Runge-Kutta 45 (RK45) with adaptive step-size control
- **Application**: Solves the 2nd-order buoy equation of motion:  

 $$(m_{\text{buoy}} + m_{\text{added}})\ddot{z} = F_{\text{wave}} + F_{\text{hydrostatic}} + F_{\text{PTO}} + F_{\text{radiation}} + F_{\text{drag}}$$

- **Features**: Automatic step adjustment during rapid force changes, maximum step size enforcement (0.5s)
- **Implementation Function**: `run_simulation()` function using `scipy.integrate.solve_ivp(method='RK45')` in the python file `simulation.py`

### Interpolation Methods:
- **Linear Interpolation**: Creates high-resolution wave elevation data from coarse measurements for continuous forcing function
- **Cubic Spline**: Generates smooth acceleration functions from discrete ODE solutions for analytical differentiation
- **Applications**: Wave data resampling, continuous function creation for root finding
- **Linear Interpolation Implementation Function**: `analyze_and_prepare_wave_data()` function using `scipy.interpolate.interp1d(kind='linear')` under `wave_processing.py`
- **Cubic Spline Implementation Function**: `find_max_acceleration()` function using `scipy.interpolate.CubicSpline()` under the python file`analysis.py`

### Root Finding:
- **Method**: Brent's method (brentq) combining bisection, secant, and inverse quadratic interpolation
- **Application**: Finds roots of jerk function $(\dddot{z} = 0)$ to identify acceleration extrema
- **Purpose**: Validates structural constraints by determining maximum acceleration values
- **Implementation Function**:  `find_max_acceleration()` function using `scipy.optimize.brentq()` under the python file`analysis.py` 

<br>

## Repository Structure

The following table show what each python file does.

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
| **`wave_elevation_data.csv`** | Raw, Real North Sea wave elevation measurements |
| **`buoy_results.png`** | Visualization of optimization results including wave elevation, forcing functions, hydrodynamic forces, buoy response, and power generation |
<br>


