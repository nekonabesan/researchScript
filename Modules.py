from shutil import which
import numpy as np
import pandas as pd
import math

from sqlalchemy import null

class Modules:
    target = null

    def __init__(self, target):
        if len(target) != 0:
            self.target = target

    def linestyle_generator(self):
        linestyle = ['-', '--', '-.', ':']
        lineID = 0
        try:
            while True:
                yield linestyle[lineID]
                lineID = (lineID + 1) % len(linestyle)
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        #except BaseException as err:
        #    print(f"Unexpected {err=}, {type(err)=}")
        #    raise

    def plot_set(self, fig_ax, *args):
        try:
            fig_ax.set_xlabel(args[0])
            fig_ax.set_ylabel(args[1])
            fig_ax.grid(ls=':')
            if len(args)==3:
                fig_ax.legend(loc=args[2])
            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        #except BaseException as err:
        #    #print(f"Unexpected {err=}, {type(err)=}")
        #    raise
    
    def bodeplot_set(self, fig_ax, *args):
        try:
            fig_ax[0].grid(which="both", ls=':')
            fig_ax[0].set_ylabel('Gain [dB]')

            fig_ax[1].grid(which="both", ls=':')
            fig_ax[1].set_xlabel('$\omega$ [rad/s]')
            fig_ax[1].set_ylabel('Phase [deg]')
            
            if len(args) > 0:
                fig_ax[1].legend(loc=args[0])
            if len(args) > 1:
                fig_ax[0].legend(loc=args[1])

            return True
        except NameError as err:
            print("NameError: {0}".format(err))
        except TypeError as err:
            print("TypeError: {0}".format(err))
        except ValueError as err:
            print("ValueError: {0}".format(err))
        except OSError as err:
            print("OS error: {0}".format(err))
        #except BaseException as err:
        #    print(f"Unexpected {err=}, {type(err)=}")
        #    raise