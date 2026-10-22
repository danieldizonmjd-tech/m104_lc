## This code fetched information from SIMBAD, which is a database
#  imports
import os
from glob import glob
import astropy.units as u                                     # niche library for astronomy, but very useful for this project
from astropy.coordinates import SkyCoord                      # ditto
from astroquery.simbad import Simbad                          # ditto

os.chdir(os.path.dirname(os.path.abspath(__file__)))          # changes directory to the location of this file

files = (glob("outputplots/flare/1_special_5sigma/*.png")+glob("outputplots/flare/2_notable_4sigma/*.png")+glob("outputplots/flare/3_interesting_3sigma/*.png")+glob("outputplots/dip/4_mild_2sigma/*.png"))
for fname in files:
    name = os.path.basename(fname).replace(".png", "")
    source, obsid = name.split("_")                           # split the name into source and obsid, which are separated by an underscore

    # split the name into RA and Dec
    s = source[1:]                                            # drop the J
    i = max(s.find("+"), s.find("-"))                         # position of the dec sign
    ra, dec = s[:i], s[i:]                                    # "123926.918" and "-114008.98"

    # rewrite as hours/minutes/seconds and degrees/arcmin/arcsec
    coord = SkyCoord(f"{ra[0:2]}h{ra[2:4]}m{ra[4:]}s {dec[0:3]}d{dec[3:5]}m{dec[5:]}s")

    # ask SIMBAD for anything within 2 arcseconds (you can do any number you want, but 2 arcseconds is a good starting point if you want to find a specific source)
    result = Simbad.query_region(coord, radius = 2 * u.arcsec)

    print(source, "ObsID", obsid)
    print(result)       # prints None if nothing was found
    print()

## end