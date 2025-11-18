import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# ---- Parameter settings ----
DT = 0.2            # sampling intervals (second)
NS = 6000           # number of data points per file
NCHAN = 3           # 3 probes

# ---- output folder ----
os.makedirs("plots", exist_ok=True)
os.makedirs("csv", exist_ok=True)

def read_one(fname):
    """read a single .DAT file"""
    raw = np.fromfile(fname, dtype=np.float32)
    if raw.size != NCHAN * NS:
        raise ValueError(f"{fname}: Expected {NCHAN*NS} 个 float32, but got {raw.size}")
    data = raw.reshape((NCHAN, NS)).T
    data -= data.mean(axis=0, keepdims=True)
    return data

def plot_one(fname, data):
    """plot wave signals for a single file"""
    t = np.arange(0, data.shape[0]*DT, DT)
    plt.figure(figsize=(9, 6))
    for i in range(NCHAN):
        plt.subplot(3, 1, i+1)
        plt.plot(t, data[:, i])
        plt.title(f"Wave Probe {i+1} — {os.path.basename(fname)}")
        plt.xlabel("Time (s)")
        plt.ylabel("Wave elevation (m)")
    plt.tight_layout()
    out_png = os.path.join("plots", os.path.basename(fname).replace(".DAT", ".png"))
    plt.savefig(out_png, dpi=150)
    plt.close()

def save_csv(fname, data):
    t = np.arange(0, data.shape[0]*DT, DT)
    out_csv = os.path.join("csv", os.path.basename(fname).replace(".DAT", ".csv"))
    header = "time_s,probe1_m,probe2_m,probe3_m"
    np.savetxt(out_csv, np.column_stack([t, data]), delimiter=",", header=header, comments="")
    return out_csv

# ---- main ----
files = sorted(glob.glob("WV*.DAT"))
if not files:
    print("No WV*.DAT files found")
else:
    all_chunks = []
    for f in files:
        d = read_one(f)
        plot_one(f, d)
        save_csv(f, d)
        all_chunks.append(d)
        print(f"Prosessed: {f}")

    # combine all files
    combined = np.vstack(all_chunks)
    t_full = np.arange(0, combined.shape[0]*DT, DT)

    # plot combined wave signals
    plt.figure(figsize=(10, 7))
    for i in range(NCHAN):
        plt.subplot(3, 1, i+1)
        plt.plot(t_full, combined[:, i])
        plt.title(f"Wave Probe {i+1} — combined {len(files)} files")
        plt.xlabel("Time (s)")
        plt.ylabel("Wave elevation (m)")
    plt.tight_layout()
    plt.savefig(os.path.join("plots", "combined.png"), dpi=150)
    plt.close()

    # Save combined CSV
    header = "time_s,probe1_m,probe2_m,probe3_m"
    np.savetxt(os.path.join("csv", "combined.csv"),
               np.column_stack([t_full, combined]),
               delimiter=",", header=header, comments="")
    print("All plots saved in ./plots and CSVs saved in ./csv")