## Makes fake light curves where I already know the answer, so I can test lightcurves.py

# This is when I did 5 ks bin 

import os
import numpy as np

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("ascii_test", exist_ok=True)

rng = np.random.default_rng(42)   # fake data is the same every time

n = 9000 # 9000 raw bins x 10 s = 90 ks
dt = 10.0 # raw bin width in seconds


def write_lc(name, counts, exposure=None):
    # script only 4 columns, so rest just stay zero
    d = np.zeros((len(counts), 8))
    d[:, 1] = np.arange(len(counts)) * dt   # start
    d[:, 3] = d[:, 1] + dt # end
    d[:, 4] = counts # counts
    d[:, 7] = dt if exposure is None else exposure   # exposure
    np.savetxt(f"ascii_test/{name}_lc_ascii.txt", d)

# should be no_event
write_lc("cons", rng.poisson(0.02, n))

# should be flare
c = rng.poisson(0.02, n)
c[4500:5000] = rng.poisson(0.08, 500)
write_lc("fl", c)

# should be dip
c = rng.poisson(0.04, n)
c[3250:3750] = 0
write_lc("d", c)

# gap: telescope off from 20-30 ks
# This should not look like dip
c = rng.poisson(0.04, n)
e = np.full(n, dt)
c[2000:3000] = 0
e[2000:3000] = 0
write_lc("g", c, e)

# should be empty

write_lc("0", np.zeros(n))

# 200 boring sources
for k in range(200):
    write_lc(f"test_null_{k:03d}", rng.poisson(0.02, n))

# both
c = rng.poisson(0.04, n)
c[3000:3500] = 0   # dip
c[6000:6500] = rng.poisson(0.10, 500)   # flare
write_lc("both", c)

## end
