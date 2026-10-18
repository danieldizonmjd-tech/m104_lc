# M104 light curves

I'm looking at Chandra X-ray light curves in the field of M104 (a.k.a. the
Sombrero Galaxy). The Python script makes plots and flags bins where the counts
look unusual. I also use Gaia and SIMBAD to see what is already known about
some of the sources. There's a separate folder with TESS data that I added to
explore.

## Project files

- `lightcurves.py` reads the ASCII light curves in `ascii_m104/`, makes plots,
  and writes `outputplots/summary.csv`.
- `gaiaquery.py` searches Gaia DR3 within 2 arcseconds of sources in the 5σ,
  4σ, and 3σ folders.
- `simbadquery.py` looks up those sources in SIMBAD.
- `outputplots/TESSTIC32449963/` contains TESS files for TIC 32449963: a FITS
  file, a CSV light curve, a plot, and an information page. I added these to
  explore; `lightcurves.py` does not make them.

## Papers

I use published papers for background on X-ray point sources, especially
sources in M104. They help me understand these objects and compare my results
with previous work. Copies are in `papers/`, including additional papers in
`papers/exppaper/`. The scripts don't use these PDFs as input.

## What the script does

The files in `ascii_m104/` have time, counts, and exposure information.
`lightcurves.py` adds the small input bins together into bins about 1 ks wide.
It compares the counts in each usable bin with what I'd expect if the source
had stayed at a constant rate. I use Poisson statistics because many bins have
only a few counts. A positive significance means more counts than expected; a
negative one means fewer.

The plots go into folders based on the largest single-bin significance:

| Output folder | Threshold |
| --- | --- |
| `0_empty/` | No counts in the input |
| `1_special_5sigma/` | At least 5σ |
| `2_notable_4sigma/` | At least 4σ but below 5σ |
| `3_interesting_3sigma/` | At least 3σ but below 4σ |
| `4_mild_2sigma/` | At least 2σ but below 3σ |
| `5_nothing_to_see_here/` | Below 2σ |

## How to read a light-curve plot

- The x-axis is time in kiloseconds; the y-axis is counts in each
  approximately 1 ks bin.
- The black step line shows the observed counts. The gray dashed step line is
  the expected counts for a constant source rate.
- Red markers flag bins whose counts differ from that expectation. An open
  circle means 2σ to less than 3σ, a filled circle means 3σ to less than 5σ,
  and a star means 5σ or greater. 
-  A `+` means more counts than expected; a
  `−` means fewer counts than expected. Bins without a red
  marker are below 2σ.
- The source and observation ID appear in the upper-left corner. An empty
  light curve instead says “0 counts in input”.

  
## Current results

The current `outputplots/summary.csv` has 357 observations of 119 source
positions:

| Tier | Observation light curves |
| --- | ---: |
| 5σ special | 2 |
| 4σ notable | 1 |
| 3σ interesting | 13 |
| 2σ mild | 177 |
| Below 2σ | 137 |
| Empty | 27 |

The biggest single-bin result is `J123945.204-113849.99_9533` at 25.04σ. Its
rough `p_global` is `9.38e-137`. The same position reaches 8.04σ in observation
`1586`. I want to look into this source, but these numbers alone don't tell me
what caused the change. `lightcurves.py` rewrites the summary when I run it.

## Source that I focused on
 *X5/HD 110086*: SIMBAD identifies this as HD 110086. Gaia has a match
  about 0.40 arcseconds away, with G magnitude 9.96, parallax 7.42 mas, and
  substantial proper motion. That fits with it being a foreground star. The
  paper by Di Stefano et al. mentions X5 as the brightest soft source. It
  also has the largest single-bin significances in my current summary: 25.04σ
  in observation 9533, 8.04σ in 1586, and 3.55σ in 9532.


## Gaia and SIMBAD follow-up

Both query scripts use source coordinates from the plots in
`1_special_5sigma/`, `2_notable_4sigma/`, and `3_interesting_3sigma/`, so I
run `lightcurves.py` first.

- `gaiaquery.py` searches Gaia DR3 within 2 arcseconds and prints matches
  ordered by distance. It asks for magnitude, parallax, proper motion, and
  RUWE. It only searches each source position once.
- `simbadquery.py` searches SIMBAD within 2 arcseconds and prints any
  catalogue identifications it finds.

The scripts print results in the terminal. I saved query results in
`outputplots/gaia.txt` and `outputplots/simbad.txt`, but running the scripts
won't update those files automatically. In the saved Gaia results, there are
two matches within 2 arcseconds; the other queried positions have no Gaia
match within that radius. Gaia's G-band data is photometry, not a spectrum.

## TESS

I also put TESS data for TIC 32449963 in `outputplots/TESSTIC32449963/`. The
target page lists sectors 10, 37, and 46. The plot shows the light curve,
phase-folded data, and a Lomb–Scargle periodogram; the listed period is about
6.5205 days. The CSV has `times`, `fluxes`, and `ferrs` columns. This is a
separate exploration, not an output of my Chandra script.

## Run

Install the Python packages used by the scripts:

```powershell
python -m pip install numpy matplotlib scipy astropy astroquery
```

From the project folder, run:

```powershell
python lightcurves.py
```

This makes the tier folders and plots and writes `outputplots/summary.csv`.
After that, I can run the Gaia and SIMBAD queries (with an internet
connection):

```powershell
python gaiaquery.py
python simbadquery.py
```

The queries can take a while if the catalogue services are busy. Results print
in the terminal.
