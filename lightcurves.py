## I will be explaining my code for a little introduction for those who may not be familiar with Python

#  setting things up in this
import os
from glob import glob
import numpy as np
import matplotlib
matplotlib.use("Agg")                                           # use Agg backend to save plots to files instead of windows
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))            # changes directory
os.makedirs("outputplots", exist_ok=True)                       # output folder for plots

bin_ks = 1 # bin width is 1 ks
files = glob("ascii_m104/*_lc_ascii.txt")                       # list of every file that ends with _lc_ascii.txt in ascii_m104

# we start a for loop to go through each file in the list of files
for fname in files:                                             # can name fname anything I want I just named it fname for file name, clever amiright? ;)
    data = np.loadtxt(fname)                                    # 2d array: rows = time bins, colums = quantities (time, counts, exposure, etc.)
    t0 = data[0, 1]                                             # next three lines will just calcuate the number of bins for rebinning
    dt = data[0, 3] - data[0, 1]
    nbin = round(bin_ks * 1000 / dt)                            # see later that bins divided to 1.0015 ks (~1.5 % difference)

    t = [0]                                                    # bin end time, starts at 0
    lc = []                                                    # holds total counts per bin, starts empty

# Raw bins hold almost no photons; rebinning pools them so real trends stand out from noise.
    for i in range(0, len(data), nbin):                        # if i is 300, the next bin will be 300 + nbin, so it will go through the whole array in steps of nbin
        part = data[i:i + nbin]
        cts = part[:, 4].sum()                                 # col 5 counts
        expo = part[:, 7].sum()                                # col 8 exposure

        if expo == 0:
            cts = np.nan                                       # no exposure nothing was observed

        lc.append(cts)
        t.append((part[-1, 3] - t0) / 1000)                    # bin end time

# make the plot
    name = os.path.basename(fname).replace("_lc_ascii.txt", "")
    plt.figure(figsize=(9, 4))
    plt.stairs(lc, t, baseline=None, color="blue", linewidth=1) #  I chose blue for the plot color but you can change it to whatever you want
    plt.xlabel("Time (ks)")
    plt.ylabel("Counts per bin")
    plt.title(f"{name} ({nbin * dt / 1000:.4f} ks bins)")
    plt.xlim(0, t[-1])
    plt.ylim(bottom=0)
    # if it is empty
    if data[:, 4].sum() == 0:
        plt.ylim(-0.1, 1)
        plt.yticks([0, 1])
        plt.text(t[-1] / 2, 0.5, "0 counts in input", ha="center")
    plt.tight_layout()
    plt.savefig(f"outputplots/{name}.png", dpi=150)
    plt.close() # free memory for next

print(f"Saved {len(files)} plots")                          # tells how many plots generated

# this was very detailed and I hope it was helpful to those who are new to Python and want to learn more about it. I will be making more of these in the future so stay tuned for that :)
## end
