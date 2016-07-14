# -*- coding: utf-8 -*-
""" Functions for characterization of the noise of a signal """

from numpy import array, fromstring, transpose, log, arange, zeros, average, \
                  exp, arctan, sqrt, sign, pi, concatenate, argmax, add, \
                  log10, diff, cos, ones, linalg, newaxis, compress, c_
from numpy.fft import fft, ifft
from numpy.random import randn
from numpy import hanning as numpy_hanning
import sys
import struct


def binfile2array(filename, typecode):
    """Reads a data file containing binary y-values into an array"""

    f = open(filename, "rb")
    a = fromstring(f.read(), typecode)
    f.close()
    if sys.platform == 'darwin':
        a = a.byteswap()
    return a


def array2binfile(a, filename):
    """Writes an array to a binary file"""

    if sys.platform == 'darwin':
        a = a.byteswap()
    f = open(filename, "wb")
    f.write(a.tostring())
    f.close()
    if sys.platform == 'darwin':
        a = a.byteswap()


def lvm2array(filename, typecode='d', separator='\t'):
        """Reads a file generated by National Instruments software
        (LVM format) into an array. The array is N*M dimensional, N the
        number of coloumns and M the number of lines in the file."""

        text = open(filename).readlines()
        while text[0][0:19] != '***End_of_Header***':
                text.pop(0)
        # That was the first header, now the second:
        text.pop(0)
        while text[0][0:19] != '***End_of_Header***':
                text.pop(0)

        # Remove '***End_of_Header***' and description line:
        text = text[2:]

        data = array([line.strip().split(separator)
                      for line in text]).astype(typecode)

        return transpose(data)


def WaveJetCSV2array(filename, typecode='d', separator='\t'):
        """Reads an ascii file saved with the LeCroy WaveJet 324 into an array.
        The array is N*M dimensional, N the number of coloumns and M the number
        of lines in the file."""

        text = open(filename).readlines()[30:]
        data = array([line.strip().split(separator)
                      for line in text]).astype(typecode)

        return transpose(data)


def WFM2array(filename, typecode='d'):
        """Reads a WFM file generated by the LeCroy waveJet 324 oscilloscope
        into an array."""

        data = ''.join(open(filename, 'rb').readlines()[199:])
        header = data[:88]
        (Npoints) = struct.unpack('>28xi56x', header)
        # Probably the number of points is not Npoints but the closest power
        # of 2 - how stupid is that


def textfile2array(filename, separator='\t', ntype='d'):
        """Reads an ascii file into an array. The array is N*M dimensional, N the
        number of coloumns and M the number of lines in the file."""

        data = [line.rstrip().split(separator)
                for line in open(filename, 'r').readlines()
                if line[0] != '#']
        data = array([line for line in data if line != ['']]).astype(ntype)
        return transpose(data)


def text2array(filename, typecode='d', separator='\t'):

        data = array([line.strip().split(separator)
                     for line in open(filename).readlines()]).astype(typecode)

        return transpose(data)


def get_dt(filename, separator='\t'):
        """Returns the time difference between samples for a measurement
        stored with National Instruments software (LVM format)."""

        f = open(filename, "r")
        line = f.readline()
        while line[0:7] != "Delta_X":
                line = f.readline()
                continue
        [text, dt] = line.strip().split(separator)
        f.close()

        return float(dt)


def crop2power2(array):
        """Returns array cropped to a length that is a power of two
        (advantageous for FFT)."""

        l = 2**int(log(len(array))/log(2))
        return array[0:l]


def centercrop2power2(array):
        """Returns an array taken from the center of 'array'. Its length is the
        maximal power of two <= len('array')."""

        l = 2**int(log(len(array))/log(2))
        l0 = len(array)
        return array[l0/2-l/2:l0/2+l/2]


def resample(x, y, N, type='lin'):
    """Resamples the arrays x and y with an arbitrary length to a
        length of N points, or len(array) if len(array)<N."""

    if len(x) != len(y):
        print("x and y need to be equally long")
        return []

    if len(y) <= N:
        return [x, y]

    if type == 'lin':
        dx = (x[-1]-x[0])/N
        resultx = arange(1.*N)*dx+x[0]+dx/2

        resulty = zeros(N).astype(y.dtype.char)
        dn = 1.*len(y)/N
        index = arange(1.*(N+1))*dn
        index = index.astype('i')
        index[-1] = len(y)
        for i in range(N):
            resulty[i] = average(y[index[i]:index[i+1]])
        return [resultx, resulty]

    if type == 'log':
        startlog = log(1.)
        endlog = log(len(y)+1)
        dlog = (endlog-startlog)/N
        logrange = arange(1.*(N+1))*dlog + startlog

        logindex = exp(logrange).astype('i')-1
        logindex[-1] = len(y)
        resulty = zeros(N).astype(y.dtype.char)
        for i in range(N):
            if logindex[i] != logindex[i+1]:
                resulty[i] = average(y[logindex[i]:logindex[i+1]])
            else:
                resulty[i] = y[logindex[i]]

        if x[0] > 0:
            startlog = log(x[0])
        else:
            startlog = log(x[1])
        endlog = log(x[-1])
        dlog = (endlog-startlog)/N
        resultx = exp(arange(1.*N)*dlog+startlog+dlog/2)
        return [resultx, resulty]

    print("type unknown!")
    return arange([])


def resamp(x, N, type='lin'):
    """Resamples the array x with an arbitrary length to a
    length of N points, or len(array) if len(array)<N."""

    if len(x) <= N:
        return x

    if type == 'lin':
        result = zeros(N).astype(x.dtype.char)
        dn = 1.*len(x)/N
        index = arange(1.*(N+1))*dn
        index = index.astype('i')
        index[-1] = len(x)
        for i in range(N):
            result[i] = average(x[index[i]:index[i+1]])
        return result

    if type == 'log':
        startlog = log(1.)
        endlog = log(len(x)+1)
        dlog = (endlog-startlog)/N
        logrange = arange(1.*(N+1))*dlog + startlog

        logindex = exp(logrange).astype('i')-1
        logindex[-1] = len(x)
        result = zeros(N).astype(x.dtype.char)
        for i in range(N):
            if logindex[i] != logindex[i+1]:
                result[i] = average(x[logindex[i]:logindex[i+1]])
            else:
                result[i] = x[logindex[i]]
        return result

    raise RuntimeError("Unknown type")


def spectrum(signal):
    """ Returns Fourier-Series coefficients, assuming that 'signal'
        represents one period of an infinitely extended periodic
        signal. """

    # A_{n, FourierSeries} = 1/L*A_{n, FFT}
    return fft(signal)/len(signal)


def ispectrum(spec):
    """ Returns the inverse fourier transform, assuming that 'spec'
        contains Fourier-Series coefficients (as generated by
        'spectrum(signal)'). """

    return ifft(spec)*len(spec)


def make_f(N, fnyquist):
    """Generates a frequency vector [-N/2, ..., +N/2-1]*2*fnyquist/N. Useful
    for FFT spectra."""

    df = 2*fnyquist/N
    return rotate(df*arange(N)-fnyquist, -N/2)


def pc_hanning(Npoints):
    """Power conserving Hanning window. """
    # WARNING: The hanning window is not RMS conserving!
    # sqrt( add.reduce(sig**2)/len(sig) ) !=
    # sqrt( add.reduce( abs(spectrum)**2 ) )
    # The window we use here is normalized so that
    # add.reduce(numpy_hanning(len)**2)/len=1
    return 1.0/sqrt(0.375)*numpy_hanning(Npoints)


def powerspectrum(signal):
    """ Powerspectrum of 'signal' in units of ['signal']^2/df"""
    return abs(spectrum(signal)[:len(signal)/2])**2


def phasor(signal):
    """ calculates the phasor of 'signal' (fft, remove
    negative frequency components, inverse_fft) """

    spec = spectrum(signal)
    spec[(len(spec)+1)/2:len(spec)] = 0
    return ifft(len(spec)*spec)


def phase(phasordata):
    """ return the phase of the complex array 'phasordata' """

    return arctan(phasordata.imag/phasordata.real) \
        + 0.5*(sign(phasordata.real) - 1) * pi


def amplitude(phasordata):
    """ returns the amplitude of the complex array 'phasordata' """

    return abs(phasordata)


def center_of_gravity(array):
    """ finds the bin nearest to the center of gravity of
    the array 'array' """

    l = len(array)
    cog = add.reduce(abs(array)*arange(l)) / add.reduce(abs(array))
    return int(cog)


def rotate(array, n=1):
    """ rotate array 'array' by 'n' elements. Written by Kevin Parks """

    n = -n
    if len(array) == 0:
        return array
    n = n % len(array)      # Normalize n, using modulo. Works for negative n
    return concatenate((array[n:], array[:n]))


def halfwidth(spec):
    maxpos = argmax(abs(spec[0:(len(spec)+1)/2]))
    x = min(maxpos, len(spec)/2-1-maxpos)
    if x == 0:
        print("halfwidth: Error: Maximum is at f=0")
    return 2**int(log(x)/log(2))


def peak_centered_spectrum(spec, halfwidth):
    if halfwidth > len(spec)/2:
        print("peak_centered_spectrum: halfwidth too large!")
        return arange(0)
    maxpos = argmax(abs(spec[0:(len(spec)+1)/2]))
    spec0 = spec[maxpos-halfwidth:maxpos+halfwidth]
    return rotate(spec0, -halfwidth)


def amplitude_phasor(signal):
    spec = spectrum(signal)
    return ifft(peak_centered_spectrum(spec))


# amlitude phasor = a(t)*exp(i*phi(t))
def phi(signal):
    return phase(amplitude_phasor(signal))


def a(signal):
    return amplitude(amplitude_phasor(signal))


def make_phase_continuous(phi):
    """ Removes 2*pi jumps from phi."""
    for i in range(len(phi)-1):
        dphi = (phi[i+1]-phi[i]) % (2*pi)
        if dphi > pi:
            dphi -= 2*pi
        phi[i+1] = phi[i] + dphi


def flatten_phase(phi):
    """ Removes 2*pi jumps from phi. Removes the linear \
    part of the phase """
    make_phase_continuous(phi)
    x = arange(len(phi))
    A = c_[x[:, newaxis], ones(len(phi))[:, newaxis]]
    [m, q], resid, rank, sigma = linalg.lstsq(A, phi)
    phi -= q + m*arange(len(phi))


def rms(signal):
    return sqrt(average((signal - average(signal))**2))


def ADC_SNR(Nbits):
    """Returns the signal-to-noise ratio (in dB) of an ideal Nbits-bit
    analog-to-digital converter."""
    return 6.02*Nbits+1.76


def ADC_NoiseFloor(Nbits, fsampling):
    """Returns the noise floor (in dBc/Hz) of an ideal Nbits-bit
    analog-to-digital converter with a sampling rate of fsampling Hz."""
    return -6.02*Nbits-1.76-10*log10(0.5*fsampling)


def unique(data):
    """Returns an array containing the values used in data
    (usefull for digitized data to find the number of levels used)."""

    copy = 1.*data
    copy.sort()
    return compress(diff(copy) > 0, copy[0:-1])


def NumberOfBitsUsed(data):
    """Returns the number of bits that have been used to digitize data."""

    return log(1.*len(unique(data)))/log(2.)


def cos_with_gaussian_noise(phi, damp_sigma, dphi_sigma, dsin_sigma):
    N = len(phi)
    damp = damp_sigma*randn(N)
    dphi = dphi_sigma*randn(N)
    dsin = dsin_sigma*randn(N)

    return (1+damp)*cos(phi+dphi)+dsin


def LP(f, f3db):
    """Low-pass filter transfer function with 3dB cut-off frequency f3db."""
    return 1./(1+f/f3db*1j)


def HP(f, f3db):
    """High-pass filter transfer function with 3dB cut-off frequency f3db."""
    return 1./(1-f3db/f*1j)


def integrate(input):
        """Return integral of the array input."""

        x = 1.*input
        for i in range(len(x)-1):
                x[i+1] = x[i]+x[i+1]
        return x
