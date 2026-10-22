# M104 light curves

Analyze Chandra X-ray light curves in the field of M104 (the Sombrero Galaxy), and explore TESS observations of HD 110086.

## Requirements

Python 3 and the following packages are required:

```powershell
python -m pip install numpy matplotlib scipy astropy astroquery lightkurve
```

The Chandra analysis expects light-curve text files matching
`ascii_m104/*_lc_ascii.txt`.

## Analyze Chandra light curves

Run the analysis from the project folder:

```powershell
python lightcurves_flares.py
```

The script combines the input data into 1 ks bins, scores count-rate deviations
using Poisson probabilities, and saves plots under `outputplots/` by event type
and significance tier. It also writes a significance-sorted
`outputplots/summary.csv`.

## Query source catalogues

After generating the plots, look up selected sources in Gaia or SIMBAD:

```powershell
python gaiaquery.py
python simbadquery.py
```

Both scripts use a 2-arcsecond search radius and print catalogue matches to
the terminal. These queries require an internet connection.

## Explore TESS data

Search for HD 110086 and download the first available SPOC light curve:

```powershell
python TESS.py
```

The script prints the TIC match and available light curves, then saves a plot
to `TESS/HD110086_TESS_lightcurve.png` when data is found. This search and
download require an internet connection.
