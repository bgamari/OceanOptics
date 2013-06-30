#!/usr/bin/env python
""" File:           example_liveview.py
    Author:         Andreas Poehlmann
    Last change:    2013/02/27

    Liveview example
"""

import OceanOptics
import time
import numpy as np

from gi.repository import Gtk, GLib

class mpl:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


class DynamicPlotter(Gtk.Window):

    def __init__(self, sample_interval=0.1, smoothing=1, oversampling=1, raw=False, size=(600,350)):
        # Gtk stuff
        Gtk.Window.__init__(self, title='OceanOptics USB2000+ Spectrum')
        self.connect("destroy", lambda x : Gtk.main_quit())
        self.set_default_size(*size)
        # Data stuff
        self.sample_interval = int(sample_interval*1000)
        self.smoothing = int(smoothing)
        self._sample_n = 0
        self.raw = bool(raw)
        self.spectrometer = OceanOptics.USB2000()
        self.wl, self.sp = self.spectrometer.acquire_spectrum()
        self.sp = np.zeros((len(self.sp), int(oversampling)))
        # MPL stuff
        self.figure = mpl.Figure()
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.grid(True)
        self.canvas = mpl.FigureCanvas(self.figure)
        self.line, = self.ax.plot(self.wl, self.sp[:,0])
        # Gtk stuff
        self.add(self.canvas)
        self.canvas.show()
        self.show_all()

    def update_plot(self):
        # -> redraw on new spectrum
        # -> average over self.sample_n spectra
        # -> smooth if self.smoothing

        # remark:
        # > smoothing can be done after averaging

        # get spectrum
        if self.raw:
            sp = np.array(self.spectrometer._request_spectrum())[20:]
        else:
            _, sp = self.spectrometer.acquire_spectrum()
        
        self.sp[:,self._sample_n] = sp
        self._sample_n += 1
        self._sample_n %= self.sp.shape[1]
        if self._sample_n == 0: # do not draw or average
            return
        # average!
        sp = np.mean(self.sp, axis=1)
        
        if self.smoothing > 1:
            n = self.smoothing
            kernel = np.ones((n,)) / n
            sp = np.convolve(sp, kernel)[(n-1):]

        self.line.set_ydata(sp)
        self.ax.relim()
        self.ax.autoscale_view(False, False, True)
        self.canvas.draw()
        return True

    
    def run(self):
        GLib.timeout_add(self.sample_interval, self.update_plot)
        Gtk.main()


if __name__ == '__main__':
    
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--raw', action='store_true', help='Show raw detector values')
    parser.add_argument('-i', '--interval', type=float, default=0.1, metavar='SECONDS',
                        help='Update interval')
    parser.add_argument('-s', '--smooth', type=int, default=1, metavar='N',
                        help='Number of spectrum points to average over')
    parser.add_argument('-O', '--oversample', type=int, default=1, metavar='N',
                        help='Average together successive spectra')

    args = parser.parse_args()

    m = DynamicPlotter(sample_interval=args.interval, raw=args.raw, smoothing=args.smooth,
                       oversampling=args.oversample)
    m.run()
