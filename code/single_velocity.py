import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- 1. select csv file ----
filename = 'csv/WV122523.csv'   

# ---- 2. read data ----
data = pd.read_csv(filename)
time = data['time_s'].values
dt = time[1] - time[0]    
wave_data = data[['probe1_m', 'probe2_m', 'probe3_m']].values

# ---- 3. calculate instant velocity ----
velocity = np.gradient(wave_data, dt, axis=0)

# ---- 4. calculate average velocity and RMS velocity ----
mean_velocity = np.mean(velocity, axis=0)
rms_velocity = np.sqrt(np.mean(velocity**2, axis=0))

print(f"✅ read {filename}")
print(f"average velocity(m/s): {mean_velocity}")
print(f"RMS velocity(m/s): {rms_velocity}")

# ---- 5. plot ----
plt.figure(figsize=(9,6))

for i in range(3):
    plt.subplot(3,1,i+1)
    plt.plot(time, velocity[:,i], label=f'Probe {i+1} velocity', color='tab:blue')
    plt.axhline(mean_velocity[i], color='red', linestyle='--', label='Mean velocity')
    plt.axhline(rms_velocity[i], color='green', linestyle=':', label='RMS level')
    plt.title(f'Instantaneous Vertical Velocity — Probe {i+1}')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (m/s)')
    plt.grid(True)
    plt.legend()

plt.tight_layout()
plt.show()

# ---- 6. save result as CSV ----
vel_df = pd.DataFrame(
    np.column_stack([time, velocity]),
    columns=['time_s','v_probe1','v_probe2','v_probe3']
)
vel_df.to_csv(filename.replace('.csv', '_velocity.csv'), index=False)
print(f"💾 saved {filename.replace('.csv', '_velocity.csv')}")
