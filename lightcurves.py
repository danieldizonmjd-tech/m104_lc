### I will be explaining my code intensively for a little introduction for those who may not be familiar with Python or this code

## Setting tools up


import os # lets us use our operating system
import csv  # reads and writes CSV files
from glob import glob # gets files / import one function
from multiprocessing import Pool # Dr. Di Stefano said this will code will be used to analyze more datasets in the future, so I am importing this to make analysis fast it basically gives a CPU core one file
# Not on Topic: pretty cool right? I am learning more about this and I rely on heavy documentation. People in ML use this.
import numpy as np # so that we can do math faster
import matplotlib # plotting
matplotlib.use("Agg")   # instead of creating windows, it gives us files
import matplotlib.pyplot as plt  # build fancier plots
from matplotlib.ticker import MultipleLocator, MaxNLocator, AutoMinorLocator  # control where the tick marks go
from scipy.stats import poisson, norm  # the statistics

##  Getting Files and conditions


os.chdir(os.path.dirname(os.path.abspath(__file__)))   # moves to the folder this to this script
bin_ks = 1  # bin width is 1 ks
# I tried 1, 5, 10 ks and no dips were detected. 1 ks focuses just on flares
USE_Multiprocessing = True

files = glob("ascii_m104/*_lc_ascii.txt")   # finds every file that ends with "_lc_ascii.txt"

## DO NOT UNCOMMENT BUT CAN REMOVE used as a reference
# This is old, I made something more efficient than this but I am keeping it so that people who have seen it before don't get confused with what I will do later in this code

# We are now going to make folders for the different tiers of light curves. The folders are named based on how significant the peak is in the light curve. The more significant the peak, the higher the tier number.
#folders = ["0_empty", "1_special_5sigma", "2_notable_4sigma", "3_interesting_3sigma", "4_mild_2sigma", "5_nothing_to_see_here"]       
#for folder in folders:
   # os.makedirs(f"outputplots/{folder}", exist_ok=True)    # exist_ok means no error

## DO NOT UNCOMMENT BUT CAN REMOVE used as a reference

## Analyze: We rebin one light curve, score every bin, save a plot, and make a csv summary


# Each file does this. When we will use Pool in the future  it lets us run many files at once
def analyze_one(fname):  # we are defining a function here
# can name fname anything I want, I just named it fname for file name, clever amiright? ;)

    data = np.loadtxt(fname)  # numpy loads in for future analyssis
    t0 = data[0, 1]  # start time
    dt = data[0, 3] - data[0, 1]  # end time minus start time
    nbin = round(bin_ks * 1000 / dt)   # how many of the bins make one 1 ks 

    t = [0] # bin edges
    lc = [] # counts total in a lightcurve
    ex = []  # exposure total

    # raw bins hold almost no photons
    for i in range(0, len(data), nbin):   # if i is 100 and nbin is 10, it will go 100, 110, 120, etc
        part = data[i:i + nbin]   # grabs the next nbin rows, this is one big bin
        cts = part[:, 4].sum()  # col 5
        expo = part[:, 7].sum()   # col 8
 
        #  telescope wasn't looking
        if expo == 0: 
            cts = np.nan  # NAN = not a number, this will be skipped

        lc.append(cts)  # save counts
        ex.append(expo) #save exposure
        t.append((part[-1, 3] - t0) / 1000)  # bin end time, we then put seconds to ks

    lc = np.array(lc, dtype=float)  # we can do math on the whole thing at once. This is a float so NaN is fine
    ex = np.array(ex, dtype=float)
    t = np.array(t)

    good = ex > 0   # True for bins where the telescope was looking
    name = os.path.basename(fname).replace("_lc_ascii.txt", "") # file name without the folder or the ending
    total = np.nansum(lc)  # nansum skips the nan bins

    peak = 0.0  # biggest sign
    p_global = np.nan  
    event_type = "empty"

    if total == 0:
        tier = "0_empty"  # nothing to analyze
    else:
        # this is why bins with less exposure don't look like fake dips
        rate = total / ex[good].sum()  
        for _ in range(5):
            keep = good & (lc <= rate * ex + 3 * np.sqrt(rate * ex) + 1)
            if keep.sum() == 0:
                break
            rate = lc[keep].sum() / ex[keep].sum()
        mu = np.where(good, rate * ex, np.nan)  
        sig = np.full(len(lc), np.nan) 

        # Notice that I used Poisson. Gaussian only works when you expect lots of counts per bin, but a lot of my bins only have 0-3.
        # I used to do a for loop here but this is much faster and probably easier to read
        

        for i in range(len(lc)):
            if not good[i]:          # telescope wasn't looking, skip
                continue
            if lc[i] >= mu[i]:       # flare side
                p = poisson.sf(lc[i] - 1, mu[i])
                sig[i] = norm.isf(max(p, 1e-300))
            else:                    # dip side
                p = poisson.cdf(lc[i], mu[i])
                sig[i] = -norm.isf(max(p, 1e-300))
        # I am going to use  a 3 sigma score to differentiate between dip, flare, both, or none
        # check for increase vs decrease
        has_flare = good & (sig >= 3)
        has_dip = good & (sig <= -3)

        if has_flare.any() and has_dip.any():
            event_type = "both"
        elif has_flare.any():
            event_type = "flare"
        elif has_dip.any():
            event_type = "dip"
        else:
            event_type = "no_event"

        # most extreme bin
        peak = np.abs(sig[good]).max()
            

        # look at enough bins and something looks weird by luck, this is a rough fix for that
        # (multiply by the number of bins we looked at)
        # TODO maybe do a proper simulation instead
        p_global = min(1.0, good.sum() * norm.sf(peak))  # min() because a probability can't go above 1
    # Remember that weird comment back from line 28 to 36? This is its replacement
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

    ## Make the plot


    plt.figure(figsize=(6.5, 3))  # width height in inches
    plt.stairs(lc, t, baseline = None, color = "black", linewidth = 0.8)     # step plot: one flat step per bin. I chose black because it looks good but you choose any color you want

    if total > 0:
        # the dashed line is what we'd see in each bin if the source never changed brightness
        plt.stairs(mu, t, baseline = None, color = "0.4", linestyle = "--", linewidth = 0.8, label = "constant-rate expectation")   # 0.4 is a dark gray

        centers = (t[:-1] + t[1:]) / 2  # middle of each bin, where markers go
        a = np.abs(sig)  # sig


        # creates icons           open o = 2-3 sigma, filled o = 3-4, diamond = 4-5, star = 5+
        red = "#b2182b"
        # nothing_to_see_here = a < 2 there is nothing unusual
        for i in range(len(centers)):
            if a[i] >= 5:
                plt.plot(centers[i], lc[i], "*", color=red, ms=11)
            elif a[i] >= 4:
                plt.plot(centers[i], lc[i], "D", color=red, ms=6)
            elif a[i] >= 3:
                plt.plot(centers[i], lc[i], "o", color=red, ms=6)
            elif a[i] >= 2:
                plt.plot(centers[i], lc[i], "o", mfc="none", mec=red, ms=6) # hollow

        # write the numbers next to the biggest bin
        j = np.nanargmax(a) # sig maximum Nan is removed
        if a[j] >= 2:
            # put the label on the left if the peak is near the right edge
            if centers[j] > 0.8 * t[-1]:
                offset = -8
                align = "right"
            else:
                offset = 8
                align = "left"

            label = rf"{lc[j]:.0f} counts, ${sig[j]:+.2f}\sigma$"
            plt.annotate(label, (centers[j], lc[j]),
                         textcoords="offset points", xytext=(offset, -3),
                         fontsize=8, ha=align)  # offset is in points
        plt.ylim(0, np.nanmax(lc) * 1.2)   # a bit of room on top so the dots don't get cut off

    # axes, lim, tick
    plt.xlabel("Time ~ ks")
    plt.ylabel(f"Counts per {bin_ks} ks bin")
    plt.xlim(0, t[-1])  # start at 0, end at the last bin
    plt.text(0.02, 0.95, name, transform=plt.gca().transAxes, va="top", fontsize=8)

    ax = plt.gca()  # gets the current axes so we can change the ticks
    ax.xaxis.set_major_locator(MultipleLocator(10))      # big tick mark every 10 ks                     
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))  # tick mark every 5 ks
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))    # 6 whole number y ticks
    ax.tick_params(which="both", direction="in", top=True, right=True)  

    # if it is empty
    if total == 0:
        plt.ylim(-0.1, 1)
        plt.yticks([0, 1])
        plt.text(t[-1] / 2, 0.5, "No Counts", ha="center")   # so you know it's empty 
    plt.tight_layout()  # stops the labels from getting cut off
    # saving to folder
    folder_path = f"outputplots/{event_type}/{tier}"
    os.makedirs(folder_path, exist_ok=True)
    plt.savefig(f"{folder_path}/{name}.png", dpi=300)# I will recommened to lower this if more datasets
    plt.close()  # free memory for next

    return (name, int(total), int(good.sum()), peak, p_global, event_type, tier)

# Run Summary Run Analysis


if __name__ == "__main__": # do this  so that we prevent infinite spawning (Windows or macOS)
    os.makedirs("outputplots", exist_ok=True)

    # run analyze_one on every file
    if USE_Multiprocessing:
        with Pool() as pool: # one worker per CPU core
            summary = pool.map(analyze_one, files) # different files per worker
    else:
        summary = [analyze_one(f) for f in files] # same

    summary.sort(key=lambda r: -r[3])   # r[3] is biggest sig, biggest is put first by -

    # you can open this csv file in excel
    with open("outputplots/summary.csv", "w", newline="") as f: # newline="" does not put blank rows
        w = csv.writer(f)
        w.writerow(["source_obsid", "total_counts", "n_bins", "peak_sigma", "p_global", "event_type", "tier"])

        for r in summary:
            w.writerow([r[0], r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.3g}", r[5], r[6]])

    # Do the same thing but terminal
    print(f"{'source':45s} {'counts':>7s} {'peak':>6s} {'p_global':>9s}  {'type':14s} tier")

    for name, total, _, peak, pg, etype, tier in summary:
        print(f"{name:45s} {total:7d} {peak:6.2f} {pg:9.3g}  {etype:14s} {tier}")

# plots generated
    print(f"\nSaved {len(files)} plots")

## coder's, author's, my note??
# I hope you were able to understand my code pretty well. I know it is long
#but if people would look at this in the future when my portion of this project is finished, I want them to understand this. 
#If any questions, contact me at danieldizon.mjd@gmail.com 
# I'll get to you soon ;)

# MJD
### end
