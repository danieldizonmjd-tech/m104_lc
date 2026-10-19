## I will be explaining my code for a little introduction for those who may not be familiar with Python
# NOTE: I did get a little help from Claude on working out the logic of the Poisson statistics
# logic and how to style the plots...

# setting things up in this
import os 
import csv  
from glob import glob 
import numpy as np 
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt  
from matplotlib.ticker import MultipleLocator, MaxNLocator, AutoMinorLocator  # control where the tick marks go
from scipy.stats import poisson, norm  # the statistics

# this is where the fun part starts

os.chdir(os.path.dirname(os.path.abspath(__file__)))   # moves to the folder this to this script
bin_ks = 1  # bin width is 1 ks
files = glob("ascii_m104/*_lc_ascii.txt")   # finds every file that ends with "_lc_ascii.txt"

# one folder per sigma
folders = ["0_empty", "1_special_5sigma", "2_notable_4sigma", "3_interesting_3sigma", "4_mild_2sigma", "5_nothing_to_see_here"]       
for folder in folders:
    os.makedirs(f"outputplots/{folder}", exist_ok=True)    # exist_ok means no error

summary = []  #one row per source 


# we start a for loop to go through each file
for fname in files:  # can name fname anything I want, I just named it fname for file name, clever amiright? ;)
    data = np.loadtxt(fname)  
    t0 = data[0, 1]  # start time
    dt = data[0, 3] - data[0, 1]  # end time minus start time
    nbin = round(bin_ks * 1000 / dt)   # how many of the bins make one 1 ks 

    t = [0]   # bin edges
    lc = []      # counts total
    ex = []      # exposure total

    # raw bins hold almost no photons
    for i in range(0, len(data), nbin):   # if i is 100 and nbin is 10, it will go 100, 110, 120, etc
        part = data[i:i + nbin]   # grabs the next nbin rows, this is one big bin
        cts = part[:, 4].sum()  # col 5
        expo = part[:, 7].sum()   # col 8
 
        # 0 => telescope wasn't looking
        if expo == 0:
            cts = np.nan  

        lc.append(cts)  # save counts
        ex.append(expo) #save exposure
        t.append((part[-1, 3] - t0) / 1000)  

    lc = np.array(lc, dtype=float)  # we can do math on the whole thing at once
    ex = np.array(ex, dtype=float)
    t = np.array(t)

    good = ex > 0   # True for bins where the telescope was looking
    name = os.path.basename(fname).replace("_lc_ascii.txt", "") # file name without the folder or the ending
    total = np.nansum(lc)  # nansum skips the nan bins

    peak = 0.0  # biggest sign
    p_global = np.nan  

    if total == 0:
        tier = "0_empty"  # nothing to analyze
    else:
        # this is why bins with less exposure don't look like fake dips
        rate = total / ex[good].sum()  
        mu = np.where(good, rate * ex, np.nan)  
        sig = np.full(len(lc), np.nan) 

        # Notice that I used Poisson. Gaussian only works when you expect lots of counts per bin, but a lot of my bins only have 0-3.
        for j in range(len(lc)):  
            if not good[j]:
                continue    # skip bins with no exposure
            k = lc[j] 
            m = mu[j] 

            if k >= m:  # a possible flare
                p = poisson.sf(k - 1, m)  # P(X >= k), the k-1 is on purpose
                sig[j] = norm.isf(max(p, 1e-300))   # max() so it never goes to oo
            else:  # a possible dip
                p = poisson.cdf(k, m)                                             
                sig[j] = -norm.isf(max(p, 1e-300))   # max() so it never goes to -oo

        peak = np.nanmax(np.abs(sig))  

        # look at enough bins and something looks weird by luck, this is a rough fix for that
        # (multiply by the number of bins we looked at)
        # TODO maybe do a proper simulation instead
        p_global = min(1.0, good.sum() * norm.sf(peak))  # min() because a probability can't go above 1

        if peak >= 5:
            tier = "1_special_5sigma"
        elif peak >= 4:
            tier = "2_notable_4sigma"
        elif peak >= 3:
            tier = "3_interesting_3sigma"
        elif peak >= 2:
            tier = "4_mild_2sigma"
        else:
            tier = "5_nothing_to_see_here"

    # make the plot
    plt.figure(figsize=(6.5, 3)) 
    plt.stairs(lc, t, baseline = None, color = "black", linewidth = 0.8)     # I chose black because it looks good but you choose any color you want

    if total > 0:
        # the dashed line is what we'd see in each bin if the source never changed brightness
        plt.stairs(mu, t, baseline = None, color = "0.4", linestyle = "--",
                   linewidth = 0.8, label = "constant-rate expectation")   # 0.4 is a dark gray

        centers = (t[:-1] + t[1:]) / 2  
        a = np.abs(sig)  


        # creates icons           open o = 2-3 sigma, filled o = 3-5, star = 5+
        red = "#b2182b"
        for level, hi, shape, fill, size in [(2, 3, "o", "none", 6), (3, 5, "o", red, 6), (5, np.inf, "*", red, 11)]:
            mask = (a >= level) & (a < hi) 
            if mask.any():  # skip it if there's nothing to show, so no empty legend entries
                plt.plot(centers[mask], lc[mask], shape, mfc=fill, mec=red, ms=size,
                         ls = "none", label=rf"$\geq {level}\sigma$")

        # write the numbers next to the biggest bin
        j = np.nanargmax(a) 
        if a[j] >= 2:
            near_right = centers[j] > 0.8 * t[-1]  # Flip the text so it stays on the plot if too close
            plt.annotate(rf"{lc[j]:.0f} counts, ${sig[j]:+.2f}\sigma$", (centers[j], lc[j]),
                         textcoords="offset points", xytext=(-8 if near_right else 8, -3),
                         fontsize=8, ha="right" if near_right else "left")  # offset is in points, not data units

        plt.ylim(0, np.nanmax(lc) * 1.2)   # a bit of room on top so the dots don't get cut off

    plt.xlabel("Time ~ ks")
    plt.ylabel(f"Counts per {bin_ks} ks bin")
    plt.xlim(0, t[-1])  # start at 0, end at the last bin
    plt.text(0.02, 0.95, name, transform=plt.gca().transAxes, va="top", fontsize=8)

    ax = plt.gca()  # gets the current axes so we can change the ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))                          
    ax.xaxis.set_minor_locator(AutoMinorLocator(5)) 
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))  
    ax.tick_params(which="both", direction="in", top=True, right=True)  

    # if it is empty
    if total == 0:
        plt.ylim(-0.1, 1)
        plt.yticks([0, 1])
        plt.text(t[-1] / 2, 0.5, "0 counts in input", ha="center")   # so you know it's empty on purpose
    plt.tight_layout()  # stops the labels from getting cut off
    plt.savefig(f"outputplots/{tier}/{name}.png", dpi=300)  # saves it in the folder for its tier
    plt.close()  # free memory for next

    summary.append((name, int(total), int(good.sum()), peak, p_global, tier))    # one row for the csv

summary.sort(key=lambda r: -r[3]) # biggest peak first (the minus flips it so big goes first)

# csv you can open in excel
with open("outputplots/summary.csv", "w", newline="") as f:  
    w = csv.writer(f)
    w.writerow(["source_obsid", "total_counts", "n_bins", "peak_sigma", "p_global", "folder"]) 
    for r in summary:
        w.writerow([r[0], r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.3g}", r[5]])  

# print info to terminal
print(f"{'source':45s} {'counts':>7s} {'peak':>6s} {'p_global':>9s}  folder")   
for name, total, _, peak, pg, tier in summary:  # _ means "I don't need this one"
    print(f"{name:45s} {total:7d} {peak:6.2f} {pg:9.3g}  {tier}")

print(f"\nSaved {len(files)} plots")

# this was very detailed and I hope it was helpful to those who are new to Python and want to learn more about it. I will be making more of these in the future so stay tuned for that :)
## end
