#!/usr/bin/env python
""" File:           integrate.py
    Author:         Ben Gamari
    Last change:    2014/08/21

    Integration example
"""

import oceanoptics
import time
import numpy as np
import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--nsamples', type=int, default=10,
                        help='number of samples to average over')
    parser.add_argument('-T', '--interval', type=float, default=0.1,
                        help='sample interval (seconds)')
    parser.add_argument('-o', '--output', default=sys.stdout,
                        help='write integrated spectrum to a file')
    parser.add_argument('-p', '--plot', action='store_true',
                        help='plot the spectrum')
    args = parser.parse_args()

    s = oceanoptics.get_a_random_spectrometer()
    s.integration_time(time_sec=args.interval*0.8)
    wl = s.wavelengths()
    accum = np.zeros_like(wl, dtype=int)
    for i in range(args.nsamples):
        sys.stderr.write('%4d / %4d\r' % (i, args.nsamples))
        accum += s.intensities()
        time.sleep(args.interval)

    out = args.output
    if out.__class__ is str:
        out = open(out, 'w')
        
    out.write('# wavelength (nm)\tintensity\n')
    np.savetxt(out, np.vstack([wl, accum]).T)

    if args.plot:
        import matplotlib.pyplot as pl
        pl.plot(wl, accum)
        pl.xlabel('wavelength (nm)')
        pl.ylabel('intensity')
        pl.show()
