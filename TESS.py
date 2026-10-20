import os
import lightkurve as lk
import matplotlib.pyplot as plt
from astroquery.mast import Catalogs

os.chdir(os.path.dirname(os.path.abspath(__file__))) # moves to where the script is

# find HD 110086 in the TESS catalog
star = "HD 110086"

matches = Catalogs.query_object(star, catalog="TIC", radius=5/3600)
matches.sort("dstArcSec") # closest match first

print(matches["ID", "ra", "dec", "dstArcSec"])

# use the closest match
tic = matches[0]["ID"]

print("HD 110086 matches TIC", tic)

# look for TESS light curves
results = lk.search_lightcurve(f"TIC {tic}", mission="TESS", author="SPOC")
print(results)

# download the first available light curve
if len(results) > 0:
    lc = results[0].download() 

    lc = lc.remove_nans() # removes missing values

    # make the plot
    lc.plot(color="black", linewidth=0.8) # lk automatically gives us a legend, it looks good so I am keepng it ;P.
    plt.title(f"TIC{tic}")
    plt.xlabel("Time ~ BTJD")
    plt.ylabel("Flux ~ e-/s")

    plt.tight_layout()
    plt.savefig("TESS/HD110086_TESS_lightcurve.png", dpi=300) # save inside TESS
    plt.show()

    print("Saved")
else:
    print("No light curves found for TIC", tic)
