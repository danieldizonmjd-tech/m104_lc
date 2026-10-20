## This code feteches information from the Gaia catalogue

# imports
import os
from glob import glob
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia # queries Gaia instead of SIMBAD

os.chdir(os.path.dirname(os.path.abspath(__file__))) # changes directory to the location of this file

files = (glob("outputplots/1_special_5sigma/*.png")+glob("outputplots/2_notable_4sigma/*.png")+glob("outputplots/3_interesting_3sigma/*.png"))

checked = set() # keeps track of sources we already searched
Gaia.ROW_LIMIT = -1  # return every candidate within the search radius (I will talk about this later)

# these are the things we want Gaia to tell us
columns = ["source_id", "ra", "dec", "phot_g_mean_mag", "parallax", "parallax_error", "parallax_over_error", "pmra", "pmra_error", "pmdec", "pmdec_error", "ruwe"]

for fname in files:
    name = os.path.basename(fname).replace("_lc_ascii.txt", "")
    source, obsid = name.split("_")  # separates the source name from the observation ID

    # the same source can appear in several observations, so only search it once
    if source in checked:
        continue
    checked.add(source)

    # split the name into RA and Dec
    s = source[1:]    # drop the J
    i = max(s.find("+"), s.find("-"))  # position of the dec sign
    ra, dec = s[:i], s[i:]

    # rewrite as hours/minutes/seconds and degrees/arcmin/arcsec
    coord = SkyCoord( f"{ra[0:2]}h{ra[2:4]}m{ra[4:]}s ", f"{dec[0:3]}d{dec[3:5]}m{dec[5:]}s", frame="icrs")

    print("\nSource:", source)

    # ask Gaia for anything within 2 arcseconds
    job = Gaia.cone_search_async(coord, radius=2 * u.arcsec, table_name="gaiadr3.gaia_source", columns=columns
    )
    result = job.get_results()    # gets the table from the query

    if len(result) == 0:
        print("Nothing found within 2 arcseconds.")
        continue

    # turn the Gaia positions into coordinates so we can compare them with ours
    gaia_coords = SkyCoord( ra=result["ra"], dec=result["dec"], unit="deg",frame="icrs")

    # calculate how far each candidate is from our source on the sky
    result["separation_arcsec"] = coord.separation(gaia_coords).arcsec
    result.sort("separation_arcsec")     # closest candidate comes first

    # print the useful columns without cutting off rows or columns
    result[["source_id", "separation_arcsec", "phot_g_mean_mag", "parallax", "parallax_error", "parallax_over_error", "pmra", "pmra_error", "pmdec", "pmdec_error", "ruwe"]].pprint(max_lines=-1, max_width=-1)

## end