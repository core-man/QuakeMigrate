# -*- coding: utf-8 -*-
"""
Module that supplies various utility functions and classes.

"""

from functools import wraps
import logging
import time

import numpy as np


log_spacer = "="*110


def make_directories(run, subdir=None):
    """
    Make run directory, and optionally make subdirectories within it.

    Parameters
    ----------
    run : pathlib Path object
        Location of parent output directory, named by run name.
    subdir : string, optional
        subdir to make beneath the run level.

    """

    run.mkdir(exist_ok=True)

    if subdir:
        new_dir = run / subdir
        new_dir.mkdir(exist_ok=True, parents=True)


def gaussian_1d(x, a, b, c):
    """
    Create a 1-dimensional Gaussian function.

    Parameters
    ----------
    x : array-like
        Array of x values
    a : float / int
        Amplitude (height of Gaussian)
    b : float / int
        Mean (centre of Gaussian)
    c : float / int
        Sigma (width of Gaussian)

    Returns
    -------
    f : function
        1-dimensional Gaussian function

    """

    f = a * np.exp(-1. * ((x - b) ** 2) / (2 * (c ** 2)))

    return f


def gaussian_3d(nx, ny, nz, sgm):
    """
    Create a 3-dimensional Gaussian function.

    Parameters
    ----------
    nx : array-like
        Array of x values
    ny : array-like
        Array of y values
    nz : array-like
        Array of z values
    sgm : float / int
        Sigma (width of gaussian in all directions)

    Returns
    -------
    f : function
        3-dimensional Gaussian function

    """

    nx2 = (nx - 1) / 2
    ny2 = (ny - 1) / 2
    nz2 = (nz - 1) / 2
    x = np.linspace(-nx2, nx2, nx)
    y = np.linspace(-ny2, ny2, ny)
    z = np.linspace(-nz2, nz2, nz)
    ix, iy, iz = np.meshgrid(x, y, z, indexing="ij")

    if np.isscalar(sgm):
        sgm = np.repeat(sgm, 3)
    sx, sy, sz = sgm

    f = np.exp(- (ix * ix) / (2 * sx * sx)
               - (iy * iy) / (2 * sy * sy)
               - (iz * iz) / (2 * sz * sz))

    return f


def logger(logstem, log):
    """
    Simple logger that will output to both a log file and stdout.

    Parameters
    ----------
    logstem : str
        Filestem for log file.
    log : bool
        Toggle for logging - default is to only print information to stdout.
        If True, will also create a log file.

    """

    if log:
        logstem.parent.mkdir(exist_ok=True, parents=True)
        handlers = [logging.FileHandler(str(logstem.with_suffix(".log"))),
                    logging.StreamHandler()]
    else:
        handlers = [logging.StreamHandler()]

    logging.basicConfig(level=logging.INFO,
                        format="%(message)s",
                        handlers=handlers)
                        # format="%(asctime)s [%(levelname)s] %(message)s",


def time2sample(time, sampling_rate):
    """
    Utility function to convert from seconds and sampling rate to number of
    samples.

    Parameters
    ----------
    time : float
        Time to convert
    sampling_rate : int
        Sampling rate of input data/sampling rate at which to compute
        the coalescence function.

    Returns
    -------
    out : int
        Time that correpsonds to an integer number of samples at a specific
        sampling rate.

    """

    return int(round(time*int(sampling_rate)))


def trim2sample(time, sampling_rate):
    """
    Utility function to ensure time padding results in a time that is an
    integer number of samples.

    Parameters
    ----------
    time : float
        Time to trim.
    sampling_rate : int
        Sampling rate of input data/sampling rate at which to compute
        the coalescence function.

    Returns
    -------
    out : int
        Time that correpsonds to an integer number of samples at a specific
        sampling rate.

    """

    return int(np.ceil(time * sampling_rate) / sampling_rate * 1000) / 1000


def timeit(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        logging.info(" "*21 + f"Elapsed time: {time.time() - ts:6f} seconds.")
        return result
    return wrap


class StationFileHeaderException(Exception):
    """Custom exception to handle incorrect header columns in station file"""

    def __init__(self):
        msg = ("StationFileHeaderException: incorrect station file header - "
               "use:\nLatitude, Longitude, Elevation, Name")
        super().__init__(msg)


class VelocityModelFileHeaderException(Exception):
    """Custom exception to handle incorrect header columns in station file"""

    def __init__(self):
        msg = ("VelocityModelFileHeaderException: incorrect velocity model "
               "file header - use:\nDepth, Vp, Vs")
        super().__init__(msg)


class ArchiveEmptyException(Exception):
    """Custom exception to handle empty archive"""

    def __init__(self):
        msg = "ArchiveEmptyException: No data was available for this timestep."
        super().__init__(msg)

        # Additional message printed to log
        self.msg = ("\t\tNo files found in archive for this time period.")


class NoScanMseedDataException(Exception):
    """
    Custom exception to handle case when no .scanmseed files can be found by
    read_coastream()

    """

    def __init__(self):
        msg = "NoScanMseedDataException: No .scanmseed data found."
        super().__init__(msg)


class NoStationAvailabilityDataException(Exception):
    """
    Custom exception to handle case when no .StationAvailability files can be
    found by read_availability()

    """

    def __init__(self):
        msg = ("NoStationAvailabilityDataException: No .StationAvailability "
               "files found.")
        super().__init__(msg)


class DataGapException(Exception):
    """
    Custom exception to handle case when all data has gaps for a given timestep

    """

    def __init__(self):
        msg = ("DataGapException: All available data had gaps for this "
               "timestep.\n    OR: no data present in the archive for the"
               "selected stations.")
        super().__init__(msg)

        # Additional message printed to log
        self.msg = ("\t\tAll available data for this time period contains gaps"
                    "\n\t\tor data not available at start/end of time period")


class ChannelNameException(Exception):
    """
    Custom exception to handle case when waveform data header has channel names
    which do not conform to the IRIS SEED standard.

    """

    def __init__(self, trace):
        msg = ("ChannelNameException: Channel name header does not conform "
               "to\nthe IRIS SEED standard - 3 characters; ending in 'Z' for\n"
               "vertical and ending either 'E' & 'N' or '1' & '2' for\n"
               "horizontal components.\n    Working on trace: {}".format(trace))
        super().__init__(msg)


class BadUpfactorException(Exception):
    """
    Custom exception to handle case when the chosen upfactor does not create a
    trace with a sampling rate that can be decimated to the target sampling
    rate

    """

    def __init__(self, trace):
        msg = ("BadUpfactorException: chosen upfactor cannot be decimated to\n"
               "target sampling rate.\n    Working on trace: {}".format(trace))
        super().__init__(msg)


class OnsetTypeError(Exception):
    """
    Custom exception to handle case when the onset object passed to QuakeScan
    is not of the default type defined in QuakeMigrate.

    """

    def __init__(self):
        msg = ("OnsetTypeError: The Onset object you have created does not "
               "inherit from the required base class - see manual.")
        super().__init__(msg)


class PickerTypeError(Exception):
    """
    Custom exception to handle case when the phase picker object passed to
    QuakeScan is not of the default type defined in QuakeMigrate.

    """

    def __init__(self):
        msg = ("PickerTypeError: The PhasePicker object you have created does"
               "not inherit from the required base class - see manual.")
        super().__init__(msg)


class TimeSpanException(Exception):
    """
    Custom exception to handle case when the user has submitted a start time
    that is after the end time.

    """

    def __init__(self):
        msg = ("TimeSpanException: The start time specified is after the end"
               " time.")
        super().__init__(msg)


class InvalidThresholdMethodException(Exception):
    """
    Custom exception to handle case when the user has not selected a valid
    threshold method.

    """

    def __init__(self):
        msg = ("InvalidThresholdMethodException: Only 'static' or 'dynamic' "
               "thresholds are supported.")
        super().__init__(msg)
