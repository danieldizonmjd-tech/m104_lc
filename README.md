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
python lightcurves.py
```

The script combines the input data into 1 ks bins, scores count-rate deviations
using Poisson probabilities, and saves plots under `outputplots/` by event type
and significance tier. It also writes a significance-sorted
`outputplots/summary.csv`.

## Check the analysis with synthetic data

The `faketest/` folder contains a repeatable fake-data generator and a small
summary checker. Run these checks in a separate copy of the project so the
synthetic inputs and generated plots do not mix with real data.

From that copy's project folder, generate the synthetic light curves and copy
them into the analysis input directory:

```powershell
python faketest\fakedata.py
Copy-Item faketest\ascii_test\*_lc_ascii.txt ascii_m104\
python lightcurves.py
```

The generator creates examples of constant, flare, dip, gap, empty, and
combined flare-and-dip light curves, plus 200 constant-rate sources. To run
the checker, copy the generated summary to the location it reads and run it:

```powershell
New-Item -ItemType Directory -Force faketest\outputplots | Out-Null
Copy-Item outputplots\summary.csv faketest\outputplots\summary.csv
python faketest\null.py
```

The checker reports whether the example event types match expectations and
how many constant-rate sources have a global probability below 0.05.

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
