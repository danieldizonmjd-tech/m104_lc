# M104 light curves

Analyze Chandra X-ray light curves in the field of M104 (the Sombrero Galaxy), and explore TESS observations of HD 110086.

## Scripts

- `lightcurves.py` bins the data in `ascii_m104/`, creates significance-tiered plots in `outputplots/`, and writes a summary CSV.
- `gaiaquery.py` and `simbadquery.py` look up selected sources in Gaia and SIMBAD. Run `lightcurves.py` first.
- `TESS.py` searches for HD 110086 and plots the first available SPOC light curve in `TESS/`.

## Run

Install dependencies:

```powershell
python -m pip install numpy matplotlib scipy astropy astroquery lightkurve
```

From the project folder, run the script you need:

```powershell
python lightcurves.py
python gaiaquery.py
python simbadquery.py
python TESS.py
```

The catalogue queries and TESS search require an internet connection.
