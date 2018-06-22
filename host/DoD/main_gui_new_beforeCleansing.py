#!/usr/bin/python3
"""
GUI for ESC P2 printer file generation

Author:     R. Waasdorp
Date:       28-12-2016
Version:    1.1


Edited June 2017 by R. Slingerland

- Print position on X axis input in microns
- standard pattern 1x1 matrix, magenta, VSD2, small dropplet
- standard printer name: xp235-ink-new

Edited November 2017 by A. Matser

- #Created a way to interlace dots in x direction for a continuous line
- Standard pattern 10x5 matrix
- Standard printer name Epson-XP-235 // Epson_Stylus_SX235
- Y position changed from 5 to 8 inch. More gives less chance that paper folds in right printer
- Added stepper movement to create diagonal lines

"""

# ---- Import modules ----
# import binascii
import math
# import copy

# for Arduino
import os
import sys
import serial

import subprocess
# import unicodedata
import string

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import simpledialog
from PIL import *#Image, ImageTk #abel

# from PIL import ImageTk, Image
# import numpy as np

from esc_functions import *
from hex_functions import *
from logos import *

from time import sleep

# =========================
# ====    CONSTANTS    ====
# =========================
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

patternSelected = 'nxm raster_diag'
printerSelected = 'SX235W'
curRow = 0

colorNames = ['black', 'black2', 'black3', 'magenta', 'cyan', 'yellow']
modUnits = [5760, 2880, 1440, 720, 360, 180, 120, 90]



# ==== DICTIONARIES ====

# PRINT METHODS IDs
pmidOpt = {
    'None' : b'',
    'Normal2' : b'\x21',
    'Normal1' : b'\x20',
    'Highres' : b'\xc0'
}

# DOT QUALITY OPTIONS
dotOpt = {
    'Economy' : b'\x10',
    'VSD1' : b'\x11',
    'VSD2' : b'\x12',
    'VSD3' : b'\x13'
}

# PRINTER MODELS + SPECS
printersParDict = {
    'SX600FW' : {'pmgmt' : 720,
                'vert': 720,
                'hor': 5760,
                'm': 5760,
                'nozzles' : 128,
                'black' : b'\x60',
                'd' : 'VSD2',
                'pmid' : 'Normal2',
                'linux-name': 'printer-sx600fw',
                'prnfiles' :'sx600fw'},
    'SX235W': {'pmgmt': 720,
                'vert': 720,
                'hor': 5760,
                'm': 5760,
                'nozzles': 30,
                'black': b'\x00',
                'black2' : b'\x05',
                'black3' : b'\x06',
                'magenta' : b'\x01',
                'cyan' : b'\x02',
                'yellow' : b'\x04',
                'd': 'VSD2',
                'pmid': 'Normal1',
                'linux-name': 'printer-sx235w',
                'prnfiles': 'sx235w'},
    'SX235W-HR': {'pmgmt': 1440,
                'vert': 1440,
                'hor': 5760,
                'm': 5760,
                'nozzles': 30,
                'black': b'\x00',
                'black2' : b'\x05',
                'black3' : b'\x06',
                'magenta' : b'\x01',
                'cyan' : b'\x02',
                'yellow' : b'\x04',
                'd': 'VSD2',
                'pmid': 'Highres',
                'linux-name': 'printer-sx235w',
                'prnfiles': 'sx235w-highres'},
    'DX6050': {'pmgmt': 720,
                'vert': 720,
                'hor': 720,
                'm': 2880,
                'nozzles': 90,
                'black': b'\x00',
                'd': 'Economy',
                'pmid': 'None',
                'linux-name': 'printer-dx6050',
                'prnfiles': 'dx6050'},
    'manual': {'pmgmt': 0,
                'vert': 0,
                'hor': 0,
                'm': 0,
                'nozzles': 0,
                'black': b'',
                'black2': b'',
                'black3': b'',
                'magenta': b'',
                'cyan': b'',
                'yellow': b'',
                'd': 'Economy',
                'pmid': 'None',
                'linux-name': 'manual',
                'prnfiles': 'manual'
               } }






# =========================
# ==== ESCP2 FUNCTIONS ====
# =========================

def p1_small(**kwargs):
    nozzlelist = createnozzlelist(29, 1, 0, fan)
    rasterdata = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_nrs(nozzlelist, color, 1) + b'\x0c'
    return rasterdata


def p1_med(**kwargs):
    nozzlelist = createnozzlelist(29, 1, 0, fan)
    rasterdata = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_nrs(nozzlelist, color, 2) + b'\x0c'
    return rasterdata


def p1_large(**kwargs):
    nozzlelist = createnozzlelist(29, 1, 0, fan)
    rasterdata = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_nrs(nozzlelist, color, 3) + b'\x0c'
    return rasterdata


def p_all_nozzles(**kwargs):
    nozzlelist = createnozzlelist(nozzles, 5, dy, 1)
    size1 = 3
    size2 = 2
    size3 = 1
    x1 = x
    x2 = x1 + rdx
    x3 = x2 + rdx
    # y = y
    raster1 = b''
    for k in range(5):
        raster1 += ESC_dollar(hor, (x1 + dx * k)) + ESC_i_nrs(nozzlelist, black, size1) + \
                   ESC_dollar(hor, (x1 + (dx * 6) + dx * k)) + ESC_i_nrs(nozzlelist, cyan, size1) + \
                   ESC_dollar(hor, (x1 + (dx * 12) + dx * k)) + ESC_i_nrs(nozzlelist, magenta, size1) + \
                   ESC_dollar(hor, (x1 + (dx * 18) + dx * k)) + ESC_i_nrs(nozzlelist, yellow, size1)
    raster2 = b''
    for k in range(5):
        raster2 += ESC_dollar(hor, x2 + dx*k) + ESC_i_nrs(nozzlelist, black, size2) + \
                   ESC_dollar(hor, x2 + (dx*6) + dx*k) + ESC_i_nrs(nozzlelist, cyan, size2) + \
                   ESC_dollar(hor, x2 + (dx*12) + dx*k) + ESC_i_nrs(nozzlelist, magenta, size2) + \
                   ESC_dollar(hor, x2 + (dx*18) + dx*k) + ESC_i_nrs(nozzlelist, yellow, size2)
        print(k)
    raster3 = b''
    for k in range(5):
        raster3 += ESC_dollar(hor, x3 + dx * k) + ESC_i_nrs(nozzlelist, black, size3) + \
                   ESC_dollar(hor, x3 + (dx * 6) + dx * k) + ESC_i_nrs(nozzlelist, cyan, size3) + \
                   ESC_dollar(hor, x3 + (dx * 12) + dx * k) + ESC_i_nrs(nozzlelist, magenta, size3) + \
                   ESC_dollar(hor, x3 + (dx * 18) + dx * k) + ESC_i_nrs(nozzlelist, yellow, size3)
    rasterdata = ESC_v(pmgmt, y) + (raster1 + raster2 + raster3) * rep + b'\x0c'
    return rasterdata


def p1_10_drops(**kwargs):
    nozzlelist = createnozzlelist(nozzles, m, dy, fan)
    raster = b''
    for k in range(10):
        raster += ESC_dollar(hor, x) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(9):
        raster += ESC_dollar(hor, x + dx) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(8):
        raster += ESC_dollar(hor, x + dx * 2) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(7):
        raster += ESC_dollar(hor, x + dx * 3) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(6):
        raster += ESC_dollar(hor, x + dx * 4) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(5):
        raster += ESC_dollar(hor, x + dx * 5) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(4):
        raster += ESC_dollar(hor, x + dx * 6) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(3):
        raster += ESC_dollar(hor, x + dx * 7) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(2):
        raster += ESC_dollar(hor, x + dx * 8) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(1):
        raster += ESC_dollar(hor, x + dx * 9) + ESC_i_nrs(nozzlelist, color, size)
    rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'
    return rasterdata


def p_raster_nxm(**kwargs):
    nozzlelist = createnozzlelist(nozzles, m, dy, fan)
    raster = b''
    for k in range(n):
        raster += (ESC_dollar(hor, (x + dx * k)) + ESC_i_nrs(nozzlelist, color, size)) * rep
    rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'
    return rasterdata

def p_raster_nxm_diag(**kwargs): # Abel fuck around
    nozzlelist = createnozzlelist(nozzles, m, dy, fan)
    raster = b''

    x_add = x + xlist[n_steps_n] / (2.54*10000)
    # x_add = 0

    print ("x base value is " + str(x * (2.54*10000)) + " micron. dx is " + str(xlist[n_steps_n]) + " micron.")

    for k in range(n):
        raster += (ESC_dollar(hor, (x_add + dx * k)) + ESC_i_nrs(nozzlelist, color, size)) * rep
        # raster += (ESC_dollar(hor, (dx * k)) + ESC_i_nrs(nozzlelist, color, size)) * rep
    rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'
    return rasterdata

def p_logo_pme_small(**kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    rasterdata = ESC_v(pmgmt, y) + (createPs(x, size=size, pmgmt=pmgmt, hor=hor, vert=vert, r=color) +
                                    createMs(x + 4 * dx, size=size, pmgmt=pmgmt, hor=hor, vert=vert, r=color) +
                                    createEs(x + 8 * dx, size=size, pmgmt=pmgmt, hor=hor, vert=vert, r=color))*rep + b'\x0c'
    return rasterdata


def p_logo_pme(**kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    rasterdata = ESC_v(pmgmt, y) + (createP(x, size=size, fn=fan, pmgmt=pmgmt, hor=hor, vert=vert, r=color) +
                                    createM(x + 6 * dx, size=size, fn=fan, pmgmt=pmgmt, hor=hor, vert=vert, r=color) +
                                    createE(x + 12 * dx, size=size, fn=fan, pmgmt=pmgmt, hor=hor, vert=vert, r=color))*rep + b'\x0c'
    return rasterdata


def p_logo_pme_mne(**kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    size1 = 3
    size2 = 1
    rasterdata = ESC_v(pmgmt, y) + (createP(x=x, r=color, size=size1, fn=fan, pmgmt=pmgmt, hor=hor, vert=vert) +
            createM(x=(x + 6 * dx), r=color, size=size1, fn=fan, pmgmt=pmgmt, hor=hor, vert=vert) +
            createE(x=(x + 12 * dx), r=color, size=size1, fn=fan, pmgmt=pmgmt, hor=hor,vert=vert) +
            createM(x=(x + dx * 20), r=color, size=size2, fn=fan, pmgmt=pmgmt, hor=hor,vert=vert) +
            createN(x=(x + 26 * dx), r=color, size=size2, fn=fan, pmgmt=pmgmt, hor=hor,vert=vert) +
            createE(x=(x + 32 * dx), r=color, size=size2, fn=fan, pmgmt=pmgmt, hor=hor,vert=vert))*rep + b'\x0c'

    return rasterdata


def p_logo_TUPME(**kwargs):
    rasterdata = printTUPME(x, y, size, color, rep, pmgmt=pmgmt, hor=hor, vert=vert)
    return rasterdata


def p_logo_TUDelft(**kwargs):
    matrix = loadlogo(2)
    rasterdata = ESC_v(pmgmt, y) + (printLOGO(matrix, x, y, size, color, pmgmt=pmgmt, hor=hor, vert=vert)) * rep + b'\x0c'
    return rasterdata


def p_logo_P(**kwargs):
    matrix = loadlogo(3)
    rasterdata = ESC_v(pmgmt, y) + (printLOGO(matrix, x, y, size, color, pmgmt=pmgmt, hor=hor, vert=vert)) * rep + b'\x0c'
    return rasterdata


def p_nxm_sml(**kwargs):
    nozzlelist = createnozzlelist(nozzles, m, dy, fan)
    # dx = 1/120
    raster1 = b''
    raster2 = b''
    raster3 = b''

    for k in range(n):
        raster1 += (ESC_dollar(hor, x + dx * k) + ESC_i_nrs(nozzlelist, color, 3)) * rep
        raster2 += (ESC_dollar(hor, x + rdx + dx * k) + ESC_i_nrs(nozzlelist, color, 2)) * rep
        raster3 += (ESC_dollar(hor, x + rdx * 2 + dx * k) + ESC_i_nrs(nozzlelist, color, 1)) * rep
    rasterdata = ESC_v(pmgmt, y) + raster1 + raster2 + raster3 + b'\x0c'
    return rasterdata


def p_raster_90x90(**kwargs):
    nozzlelist = createnozzlelist(nozzles, 30, 0, 0)
    # dx = um_in(200)
    # size = int(input('size [1/2/3]: '))
    raster1 = b''
    raster2 = b''
    raster3 = b''
    for k in range(90):
        raster1 += (ESC_dollar(hor, x + dx * k) + ESC_i_nrs(nozzlelist, black, size)) * rep
        raster2 += (ESC_dollar(hor, x + dx * k) + ESC_i_nrs(nozzlelist, black2, size)) * rep
        raster3 += (ESC_dollar(hor, x + dx * k) + ESC_i_nrs(nozzlelist, black3, size)) * rep
    rasterdata = ESC_v(pmgmt, y) + raster1 + raster2 + raster3 + b'\x0c'
    return rasterdata


def p_1_100_drops(**kwargs):
    nozzlelist = createnozzlelist(nozzles, n, dy, fan)
    raster = b''
    for k in range(100):
        raster += ESC_dollar(hor, x) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(80):
        raster += ESC_dollar(hor, x + dx) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(60):
        raster += ESC_dollar(hor, x + dx * 2) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(40):
        raster += ESC_dollar(hor, x + dx * 3) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(20):
        raster += ESC_dollar(hor, x + dx * 4) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(10):
        raster += ESC_dollar(hor, x + dx * 5) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(5):
        raster += ESC_dollar(hor, x + dx * 6) + ESC_i_nrs(nozzlelist, color, size)
    for k in range(1):
        raster += ESC_dollar(hor, x + dx * 4) + ESC_i_nrs(nozzlelist, color, size)
    rasterdata = ESC_v(pmgmt, y) + raster + b'\x0c'
    return rasterdata


def p_logo_TU_fast(**kwargs):
    # stretch = int(input('horizontal stretch between dots (def=3): '))
    rasterdata = ESC_v(pmgmt, y) + ESC_dollar(hor, x) + ESC_i_matrix(color, load_logo_fast(), stretch, size, fan) + b'\x0c'
    return rasterdata






# =============================
# ==== CHARACTER FUNCTIONS ====
# =============================


def createPs(x, r=b'\x00', size=1, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5])
    list2 = createnozzlelistsp(29, [1, 3])
    list3 = createnozzlelistsp(29, [1, 2, 3])
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createMs(x, size=1, r=b'\x00', **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5])
    list2 = createnozzlelistsp(29, [2])
    list3 = createnozzlelistsp(29, [1, 2, 3, 4, 5])
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createEs(x, r=b'\x00', size=1, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5])
    list2 = createnozzlelistsp(29, [1, 3, 5])
    list3 = createnozzlelistsp(29, [1, 5])
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createP(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [1, 4], fn)
    list3 = list2
    list4 = list2
    list5 = createnozzlelistsp(29, [2, 3], fn)
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createE(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [1, 4, 7], fn)
    list3 = list2
    list4 = list2
    list5 = createnozzlelistsp(29, [1, 7], fn)
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createM(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [2], fn)
    list3 = createnozzlelistsp(29, [3, 4], fn)
    list4 = list2
    list5 = list1
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createN(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [3], fn)
    list3 = createnozzlelistsp(29, [4], fn)
    list4 = createnozzlelistsp(29, [5], fn)
    list5 = list1
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createD(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [1, 7], fn)
    list3 = list2
    list4 = list2
    list5 = createnozzlelistsp(29, [2, 3, 4, 5, 6], fn)
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createL(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [7], fn)
    list3 = list2
    list4 = list2
    list5 = list2
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createF(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list2 = createnozzlelistsp(29, [1, 4], fn)
    list3 = list2
    list4 = list2
    list5 = createnozzlelistsp(29, [1], fn)
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createT(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1], fn)
    list2 = list1
    list3 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6, 7], fn)
    list4 = list1
    list5 = list1
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def createU(x, r=b'\x00', size=1, fn=0, **kwargs):
    dy = 0
    dx = (dy + 1) * (1 / 120)
    hor = 5760

    list1 = createnozzlelistsp(29, [1, 2, 3, 4, 5, 6], fn)
    list2 = createnozzlelistsp(29, [7], fn)
    list3 = list2
    list4 = list2
    list5 = list1
    m = len(list1)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    image = ESC_dollar(hor, x) + ESC_i_nrs(list1, r, size) + \
            ESC_dollar(hor, x + dx) + ESC_i_nrs(list2, r,size) + \
            ESC_dollar(hor,x + 2 * dx) + ESC_i_nrs(list3, r, size) + \
            ESC_dollar(hor, x + 3 * dx) + ESC_i_nrs(list4, r, size) + \
            ESC_dollar(hor,x + 4 * dx) + ESC_i_nrs(list5, r, size)

    # suffix1 = b'\x0d' #b'\x0d\x0c'
    total = image

    return total


def printTUDELFT(x=5, y=3, size=3, **kwargs):
    pmgmt = 720
    hor = 5760
    vert = 720
    black = b'\x00'
    dy = 0
    dx = (dy + 1) * (1 / 120)
    size1 = size
    size2 = size

    rasterdata = ESC_v(pmgmt, y) + \
                 createT(x, black, size1) + \
                 createU(x + 6 * dx, black, size1) + \
                 createD(x + 18 * dx,black,size1) + \
                 createE(x + dx * 24, black, size2) + \
                 createL(x + 30 * dx, black, size2) + \
                 createF(x + 36 * dx, black, size2) + \
                 createT(x + 42 * dx, black, size2) + b'\x0c'
    return rasterdata


def printTUPME(x=5, y=3, size=3, color=b'\x00', rep=1, **kwargs):
    pmgmt = 720
    hor = 5760
    vert = 720
    black = color
    dy = 0
    dx = (dy + 1) * (1 / 120)
    size1 = size
    size2 = size

    rasterdata1 = createT(x, black, size1) + \
                  createU(x + 6 * dx, black, size1) + \
                  createD(x + 18 * dx, black, size1) + \
                  createE(x + dx * 24, black, size1) + \
                  createL(x + 30 * dx, black, size1) + \
                  createF(x + 36 * dx, black, size1) + \
                  createT(x + 42 * dx, black, size1)
    rasterdata2 = createP(x, black, size1, 10) + \
                  createM(x + 6 * dx, black, size1, 10) + \
                  createE(x + 12 * dx, black, size1, 10) + \
                  createM(x + dx * 20, black, size2, 10) + \
                  createN(x + 26 * dx, black, size2, 10) + \
                  createE(x + 32 * dx, black, size2, 10)

    rasterdata = ESC_v(pmgmt, y) + (rasterdata1 + rasterdata2)*rep + b'\x0c'  
    return rasterdata


def printLOGO(matrix, x=5.5, y=3, size=3, r=b'\x00', **kwargs):
    pmgmt = 720
    hor = 5760
    vert = 720
    color = r
    dy = 0
    dx = (dy + 1) * (1 / 120)
    rasterdata = b''
    for k in range(len(matrix)):
        rasterdata += (ESC_dollar(hor, x + k * dx) + ESC_i_nrs(matrix[k], color, size))
    image = rasterdata
    return image


# =============================
# === LINE FUNCTIONS ABEL =====
# =============================
print("Start of line functions setup")
def line_diag ():
    global n_steps_round, xlist, ylist, xylist
    global x, y, x1, y1, x2, y2, Dx, Dy
    global d_overlap, d_overlap_y #use it for single step of stepper

    print("start line_diag")

    ### Variables ### which units are they in? programmed for microns. Verify!
    # manual
    x1=0
    y1=0

    x2=100 #for vertical lines use x1+1
    y2=20 * 40

    # #terminal
    # x1 = int(input("Please enter x1 \n"))
    # y1 = int(input("Please enter y1 \n"))

    # x2 = int(input("Please enter x2 \n"))
    # y2 = int(input("Please enter y2 \n"))

    Dy=y2-y1 #total difference y
    Dx=x2-x1 #total difference x

    # Droplet size
    d = 80 #micron
    d_overlap = 0.5*d #d_overlap_y

    ### Calculations ### #use python3!
    a = (Dy / Dx) # Slope
    b = y1 - x1 * a

    # Diagonal lines
    lineLength = math.sqrt(Dx**2 + Dy**2)
    n_steps = lineLength / d_overlap
    n_steps_round = math.ceil(n_steps)
    # Vertical step size
    d_overlap_y = Dy / lineLength * d_overlap
    # Horizontal step size - is not used
    # d_overlap_x = Dx / lineLength * d_overlap

    ### Usage ###
    #y=ax+b -> x=(y-b)/a
    xlist = []
    ylist = []
    for k in range(n_steps_round+1):
        y= k*d_overlap_y + y1
        ylist.insert(k,y)

        x = (y-b) / a # Possible to use different functions for different lines
        xlist.insert(k,x)

    xylist = [xlist, ylist] # to get fifth y value call xylist[1][4]

    # for x,y in zip(xlist,ylist):
    #     print("(x,y): (" + str(x) + "," + str(y) + ")")
    print("end line_diag")
line_diag()

def arduino_init():
    global operatingSystem
    global arduino
    global timeToPrint, timeToStep

    #Operating system choice
    #Linux = 1
    #Windows = 2
    #Necessary for Arduino settings
    if str(sys.platform) == "win32":
        operatingSystem = 2
        print("OS Windows 32")
    elif str(sys.platform) == "linux":
        operatingSystem = 1
        print("OS Linux")
    else: 
        operatingSystem = input('Select operating system number: Linux (1), Windows 32 (2): ')

    print("start arduino_init()")
    
    # Path Arduino
    linuxpathList = []
    linuxpathList = [ "/dev/ttyUSB0" , "/dev/ttyUSB1" , "/dev/ttyACM0" , "/dev/ttyACM1" ]
    linuxpath = linuxpathList[2]

    if operatingSystem == 1:
        ### NEW ###
        for k in range(len(linuxpathList)):
            try:
                arduino = serial.Serial(linuxpathList[k])
                if arduino.is_open == 1:                    
                    print("USB connection to Arduino working for " + str(linuxpathList[k]))
                    linuxpath=linuxpathList[k]
                    k = len(linuxpathList)
            except:
                print( "USB connection to Arduino NOT working for " + str(linuxpathList[k]))

        ### OLD ###
        # arduino = serial.Serial(linuxpath)
        # linuxpath = linuxpathList[k]
        # linuxpath = "/dev/ttyACM1"
        
    elif operatingSystem == 2:
        arduino = serial.Serial('COM3')
    else:
        print("Select operating system")

    timeToPrint = 18 # measure this before printing, otherwise you will move arduino while printer is still printing
    #maybe have this depend on done signal of lp?
    timeToStep = 3

    # global operatingSystem
    # global arduino
    # global timeToPrint, timeToStep

    # print("start arduino_init()")
    # # Path arduino
    # linuxpath0="/dev/ttyUSB0"
    # linuxpath1="/dev/ttyUSB1"
    # linuxpath2="/dev/ttyACM0"
    # linuxpath3="/dev/ttyACM1"
    # linuxpath=linuxpath2
    # # test which path is available ABEL

    # # ONLY FOR LINUX
    # arduino = serial.Serial(linuxpath)
    # operatingSystem=1
    
    # timeToPrint = 18 # measure this before printing, otherwise you will move arduino while printer is still printing
    # #maybe have this depend on done signal of lp?
    # timeToStep = 3

arduino_init()

def sendtoArduino():
    print("sendtoArduino")
    
    print(arduino.name)

    sleepTime(0.1, "Arduino")
    
    if arduino.is_open == 1:                    
        print("USB connection to Arduino working")   # no conflict on usb
    else:
        print("Open up Arduino!")
        arduino.open()
        sleepTime(timeToStep, "Arduino")
        if arduino.is_open == 1:                    
            print("USB connection to Arduino working")   # no conflict on usb
        else:
            print( "USB connection to Arduino NOT working")
    
    sleepTime(0.2, "Arduino")
    
    try:
        print("Read Arduino")
        # start = arduino.readline().decode().strip() # can give errors
        # print("Arduino: " + start)
    except:
        print("Port " + arduino.name + " NOT really open.")

    translationRate = 500 #one rotation is 500 microns
    stepsperRotation = 200*16 #one rotation is 200*16=3200 steps using the NEMA-17 stepper motor
    
    if n_steps_n == 0:
        steps = 0
    elif n_steps_n > 0:
        steps = round((d_overlap_y)/translationRate*stepsperRotation)
    
    distanceStr = str(steps)
    print ("steps to travel: " + distanceStr + ". Now at location " + str(n_steps_n*steps))
    
    
    arduino.write(distanceStr.encode()) #newpos is the variable distance to travel
    sleepTime(timeToStep, "stepping")
    arduino.close()  # when stepping multiple times, gives errors
    print ("usb closed, program finished")
    

def tkinter_show_line():
    ### tkinter ###

    master = Tk()

    w = Canvas(master, width=Dx, height=Dy)
    w.pack()

    w.create_line(x1-x1, y1-y1, x2-x1, y2-y1)

    for x,y in zip(xlist,ylist):
        w.create_line(x-x1-5,y-y1,x-x1+5,y-y1, fill="red") # to check if dots are placed right


    mainloop()
#tkinter_show_line()

def arduinoLoop():
    #if arduino necessary send 
    sendtoArduino()
    
def sleepTime(time, text):
    print("--- Start, now wait " + str(time) + " seconds for " + text + ".")
    sleep(time)
    print("--- End of waiting for " + text + ".")

print("End of line functions setup")
    







## LOAD BITMAP FUNCTIONS

# def load_bitmap1(**kwargs):
#     def open_image(event=None):
#     #     global img_dir
#         img_dir_tot = filedialog.askopenfile()
#         img_dir = img_dir_tot.name
#         IMG = Image.open(img_dir)
#         loadbtmp.lift()
#         Canvas1.image = ImageTk.PhotoImage(IMG)
#         Canvas1.create_image(0, 0, image=Canvas1.image, anchor='nw')
#
#     loadbtmp = tk.Toplevel()
#     tk.Tk.wm_title(loadbtmp, "Load bitmap")
#
#     frame_bitmap = ttk.Frame(loadbtmp)
#     frame_bitmap.pack()
#
#     # img_dir = filedialog.askopenfile()
#     # img_dir = "C:\\Users\\rickw\\Desktop\\test.jpg"
#     # IMG = Image.open(img_dir)
#
#
#     LoadImgBtn = ttk.Button(frame_bitmap, text="Open Image", command=open_image)
#     LoadImgBtn.pack()
#
#     Canvas1 = tk.Canvas(loadbtmp, width=200, height=200)
#     Canvas1.pack()
#     # photo = ImageTk.PhotoImage(IMG)
#     # w = tk.Label(loadbtmp, image=photo)
#     # w.photo = photo
#     # w.pack()
#     # Canvas1.image = ImageTk.PhotoImage(IMG)
#     # Canvas1.create_image(0, 0, image=Canvas1.image, anchor='nw')
#
#
#
#
#     loadbtmp.resizable(0, 0)
#     loadbtmp.mainloop()






# ==============================================
# ==============================================
# |||                                        |||
# |||             BEGIN GUI                  |||
# |||                                        |||
# ==============================================
# ==============================================

def nothing(event=None):
    pass


# ---- Initialisation of Contstants
patterns={}
def load_patterns(event=None):
    global patterns
    patterns = {
        # 'Load Bitmap':{'posx':      [True, 14],
        #             'posy':         [True, 5],
        #             'dx':           [False, 250],
        #             'dy':           [False, 0],
        #             'rdx':          [False, 0],
        #             'widthn':       [False, 6],
        #             'heightm':      [False, 10],
        #             'dropsize':     [False, 1],
        #             'fan':          [False, 0],
        #             'rep':          [True, 1],
        #             'stretch':      [True, 3],
        #             'color':        [True, 'black'],
        #             'command':      [nothing, 0]},
        'nxm raster' : {'posx':     [True, 166000],
                    'posy':         [True,8], # Abel changed
                    'dx':           [True, 250],
                    'dy':           [True, 0],
                    'rdx':          [False, 0],
                    'widthn':       [True, 10],
                    'heightm':      [True, 4],
                    'dropsize':     [True, 1],
                    'fan':          [True,0],
                    'rep':          [True,1],
                    'stretch':      [False,0],
                    'color' :       [False,'magenta'],
                    'command' :     [p_raster_nxm,0]},

        'nxm raster_diag' : {'posx':     [True, 166000], #Abel addition to fuck around
                    'posy':         [True,8], # Abel changed
                    'dx':           [True, 250],
                    'dy':           [True, 0],
                    'rdx':          [False, 0],
                    'widthn':       [True, 5],
                    'heightm':      [True, 1],
                    'dropsize':     [True, 1],
                    'fan':          [True,0],
                    'rep':          [True,1],
                    'stretch':      [False,0],
                    'color' :       [False,'black'],
                    'command' :     [p_raster_nxm_diag,0]},
        
        '90x90 raster' : {'posx':   [True, 166000],
                    'posy':         [True,5],
                    'dx':           [True, 211.6666666666667],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 90],
                    'heightm':      [False, 90],
                    'dropsize':     [True, 1],
                    'fan':          [False,0],
                    'rep':          [True,1],
                    'stretch':      [False,0],
                    'color' :       [False,'magenta'],
                    'command' :     [p_raster_90x90,0]},
        
        'all nozzles' : {'posx':     [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [True, 250],
                    'dy':           [True, 1],
                    'rdx':          [True, 5000],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [False, 1],
                    'fan':          [False, 0],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [False, 'magenta'],
                    'command' :     [p_all_nozzles, 0]},
        
        '1-10 drops stacked' : {'posx': [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [True, 500],
                    'dy':           [True, 2],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [True, 3],
                    'dropsize':     [True, 1],
                    'fan':          [True, 1],
                    'rep':          [False, 1],
                    'stretch':      [False, 0],
                    'color' :       [False, 'magenta'],
                    'command' :     [p1_10_drops, 0]},
        
        'raster nxm all dropsizes': {'posx': [True, 166000],
                     'posy':        [True, 5],
                     'dx':          [True, 250],
                     'dy':          [True, 0],
                     'rdx':         [True, 5000],
                     'widthn':      [True, 6],
                     'heightm':     [True, 10],
                     'dropsize':    [False, 1],
                     'fan':         [True, 0],
                     'rep':         [True, 1],
                     'stretch':     [False, 0],
                     'color':       [True, 'magenta'],
                     'command':     [p_nxm_sml, 0]},
        
        'logo PME small' : {'posx': [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [False, 0],
                    'rep':          [False, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_pme_small, 0]},
        
        'logo PME' : {'posx':       [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [True, 0],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_pme, 0]},
        
        'logo PME-MNE' : {'posx':   [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [False, 1],
                    'fan':          [True, 1],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_pme_mne, 0]},
        
        'logo TU-PME' : {'posx':    [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [False, 0],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_TUPME, 0]},
        
        'logo TUDELFT' : {'posx':   [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [False, 0],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_TUDelft, 0]},
        
        'logo P' : {'posx':   [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 0],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [False, 0],
                    'rep':          [True, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_P, 0]},
        
        '1-100 drops stacked' : {'posx': [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [True, 3],
                    'rdx':          [True, 2500],
                    'widthn':       [False, 6],
                    'heightm':      [True, 5],
                    'dropsize':     [True, 1],
                    'fan':          [True, 0],
                    'rep':          [False, 1],
                    'stretch':      [False, 0],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_1_100_drops, 0]},
        
        'logo TU-FAST' : {'posx':   [True, 166000],
                    'posy':         [True, 5],
                    'dx':           [False, 250],
                    'dy':           [False, 0],
                    'rdx':          [False, 5000],
                    'widthn':       [False, 6],
                    'heightm':      [False, 10],
                    'dropsize':     [True, 1],
                    'fan':          [True, 0],
                    'rep':          [True, 1],
                    'stretch':      [True, 3],
                    'color' :       [True, 'magenta'],
                    'command' :     [p_logo_TU_fast, 0]},
        # 'znew3' : {'posx':            [False, 14],
        #             'posy':         [False, 5],
        #             'dx':           [False, 250],
        #             'dy':           [False, 0],
        #             'rdx':          [False, 5000],
        #             'widthn':       [False, 6],
        #             'heightm':      [False, 10],
        #             'dropsize':     [False, 1],
        #             'fan':          [False, 0],
        #             'rep':          [False, 1],
        #             'stretch':      [False, 0],
        #             'color' :       [False, 'black'],
        #             'command' :     [p_raster_nxm, 0]},
    }

load_patterns()


pmidNames = ()
for x in pmidOpt:
    pmidNames += (x,)


dotNames = ()
for x in dotOpt:
    dotNames += (x,)
dotNames = tuple(sorted(dotNames))



def nR():
    global curRow
    curRow += 1
    return curRow


def sR():
    global curRow
    return curRow


def nsy(event=None):
    print('not supported yet')


def addEntry(destframe, desc, unit, value, rown, coln=0, valcmd=None):

    label_new = ttk.Label(destframe, text=(desc+": "))
    entry_new = ttk.Entry(destframe, textvariable=value, validate = 'key', validatecommand = valcmd, justify = tk.LEFT, width=13)
    label_new_unit = ttk.Label(destframe, text=" "+unit)
    label_new.grid(row=rown, column=coln, sticky="e", pady=2)
    entry_new.grid(row=rown, column=coln+1, pady=2, padx=5, sticky="e")
    label_new_unit.grid(row=rown, column=coln+2, sticky="w", pady=2)


def addOption(destframe, desc, value, vlist, rown, coln=0, valcmd=None):

    label_new = ttk.Label(destframe, text=(desc+": "))
    combobox_new = ttk.Combobox(destframe, values=vlist, textvariable=value, width=10, validate = 'key', validatecommand = valcmd, justify = tk.LEFT)
    # label_new_unit = ttk.Label(destframe, text=" "+unit)
    label_new.grid(row=rown, column=coln, sticky="e", pady=2)
    combobox_new.grid(row=rown, column=coln+1, pady=2, padx=5)
    # label_new_unit.grid(row=rown, column=coln2, sticky="w", pady=2)


def validate_int(action, index, value_if_allowed,
                   prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if (action == '1'):
        if text in '0123456789.':
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


def validate_float(action, index, value_if_allowed,
                   prior_value, text, validation_type, trigger_type, widget_name):
    # action=1 -> insert
    if (action == '1'):
        if text in '0123456789.':
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False
    else:
        return True


# dout = dict((k,v) for k,v in mydict.items())
def setvar_dict(originaldict):
    # dict1 = copy.deepcopy(originaldict)
    dict1 = originaldict.copy()
    for x in dict1:
        if dict1[x][0] == True:
            value = dict1[x][1]
            if isinstance(value, tk.IntVar) or isinstance(value, tk.StringVar) or \
                    isinstance(value, tk.DoubleVar) or isinstance(value, tk.BooleanVar):
                pass
                # print('  Already Correct Var!')
            elif isinstance(value, int):
                dict1[x][1] = tk.IntVar()
                dict1[x][1].set(value)
                # print('  Done!')
            elif isinstance(value, float):
                dict1[x][1] = tk.DoubleVar()
                dict1[x][1].set(value)
                # print('  Done!')
            elif isinstance(value, bool):
                dict1[x][1] = tk.BooleanVar()
                dict1[x][1].set(value)
                # print('  Done!')
            elif isinstance(value, str):
                dict1[x][1] = tk.StringVar()
                dict1[x][1].set(value)
                # print('  Done!')
            elif isinstance(value, bytes):
                print('  setvar_dict() is NOT SUPPORTED YET ;(')
            else:
                print('  NOT SUPPORTED YET ;( (maybe wrong dict1 type...)')
        else:
            pass
    return dict1


def setvar_printer_dict(originaldict):
    dict1 = originaldict.copy()
    for x in dict1:
        value = dict1[x]
        if isinstance(value, tk.IntVar) or isinstance(value, tk.StringVar) or \
                isinstance(value, tk.DoubleVar) or isinstance(value, tk.BooleanVar):
            pass
            # print('  Already Correct Var!')
        elif isinstance(value, int):
            dict1[x] = tk.IntVar()
            dict1[x].set(value)
            # print('  Done!')
        elif isinstance(value, float):
            dict1[x] = tk.DoubleVar()
            dict1[x].set(value)
            # print('  Done!')
        elif isinstance(value, bool):
            dict1[x] = tk.BooleanVar()
            dict1[x].set(value)
            # print('  Done!')
        elif isinstance(value, str):
            dict1[x] = tk.StringVar()
            dict1[x].set(value)
            # print('  Done!')
        elif isinstance(value, bytes):
            print('  NOT SUPPORTED YET ;( in def setvar_printer_dict()')
        else:
            print('  NOT SUPPORTED YET ;( (maybe wrong dict1 type...)')
    return dict1


def slugify(file_name):
    file_name = file_name.replace(' ', '_')
    print(file_name)
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in file_name if c in valid_chars)



# =============================
# ---- Main GUI Class ----
# =============================
root = tk.Tk()
# ICON AND TITLE
# tk.Tk.iconbitmap(root, default="icons\clienticon.ico")
tk.Tk.wm_title(root, "ESC/P2 Control Client (for Drop-on-demand)") #Abel: currently not as default nxm is not 1x1


# =============================
# STYLE
# =============================
s = ttk.Style()
s.configure('Blue.TLabelframe.Label', font=('Verdana', 14))
s.configure('Blue.TLabelframe.Label', foreground='royal blue')
s.theme_use('clam')
# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')


# =============================
# FRAMES IN MAIN FRAME (NOTEBOOK)
# =============================
main_frame = ttk.Notebook(root)
print_frame = ttk.Frame(main_frame)
calibrate_frame = ttk.Frame(main_frame)
setup_frame = ttk.Frame(main_frame)

main_frame.add(print_frame, text='  Print  ')
main_frame.add(calibrate_frame, text='  Calibrate  ')
main_frame.add(setup_frame, text='  Settings  ')

main_frame.pack(side="top", fill="both", expand=True)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)



# =============================
# FRAMES IN PRINT MENU
# =============================
frame_patterns = ttk.Labelframe(print_frame, padding=6, text="Patterns", style="Blue.TLabelframe")
frame_printers = ttk.Labelframe(print_frame, padding=6, text="Printers", style="Blue.TLabelframe")
frame_patterns_par = ttk.Labelframe(print_frame, padding=6, text="Set Pattern Parameters", style="Blue.TLabelframe")
frame_printers_par = ttk.Labelframe(print_frame, padding=6, text="Set Printer Parameters", style="Blue.TLabelframe")
frame_controls = ttk.Labelframe(print_frame, padding=6, text="Control", style="Blue.TLabelframe")

frame_patterns.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
frame_printers.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
frame_patterns_par.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
frame_printers_par.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
frame_controls.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

# size frames
print_frame.grid_columnconfigure(1, minsize=1000)
# print_frame.grid_columnconfigure(2, minsize=300)


# print_toolbar = ttk.Frame(print_frame, width=300, padding=5)
# print_varsetup = ttk.Frame(print_frame, width=800)
# print_toolbar.grid(row=0, column=0, sticky="nsew")
# ttk.Separator(print_frame, orient="vertical").grid(row=0,column=1, sticky="ns")
# print_varsetup.grid(row=0, column=2, sticky="nsew")




# =============================
# FRAME IN SETUP
# =============================
setup_main = ttk.Frame(setup_frame)
setup_main.pack()
ttk.Label(setup_main, text="EMPTY", font=LARGE_FONT).pack()


# =============================
# FRAME IN Calibrate
# =============================
calibrate_main = ttk.Frame(calibrate_frame)
calibrate_main.pack()
ttk.Label(calibrate_main, text="Place GUI over here", font=LARGE_FONT).pack()




# =============================
# MENUBAR
# =============================
menubar = tk.Menu(main_frame)
tk.Tk.config(root, menu=menubar)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Save current as preset", command=lambda: nsy())
filemenu.add_command(label="Set Save location", command=lambda: set_save_dir())
filemenu.add_command(label="Reset Parameters", command=lambda: reset_vars())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)
menubar.add_cascade(label="File", menu=filemenu)

linuxmenu = tk.Menu(menubar, tearoff=0)
linuxmenu.add_command(label="Print to default printer", command=lambda: print_esc_commands())
linuxmenu.add_command(label="Print to printer...", command=lambda: print_esc_commands(PLNAME='other'))
linuxmenu.add_separator()
linuxmenu.add_command(label="Cancel All printjobs", command=lambda: cancel_print_jobs())
# linuxmenu.add_command(label="Restart Cups", command=lambda: restart_cups())
linuxmenu.add_separator()
linuxmenu.add_command(label="Parse ESC/P2", command=lambda: parse_escp2())
linuxmenu.add_command(label="Unprint", command=lambda: unprint_escp2())
menubar.add_cascade(label="Linux Tools", menu=linuxmenu)

# newmenu = tk.Menu(menubar, tearoff=0)
# newmenu.add_command(label="new item", command=lambda: nsy())
# menubar.add_cascade(label="new menu", menu=newmenu)

helpMenu = tk.Menu(menubar, tearoff=0)
helpMenu.add_command(label="Open manual (pdf)", command=lambda: open_help_pdf())
menubar.add_cascade(label="Help", menu=helpMenu)



# =============================
# SET PATTERN PRESETS
# =============================

dy_var = tk.StringVar()
def updateDyVar(event=None):
    dy_num = (patternDict['dy'][1].get()+1)*211.6666666666667
    dy_var.set('= '+str("%.2f" % round(dy_num,2))+u' \u03bcm')



# =============================
# PATTERN SELECT LISTBOX
# =============================
patternList = ()
for x in patterns:
    patternList += (x,)

patNames = tk.StringVar(value=tuple(patternList))
patList = tk.Listbox(frame_patterns, listvariable=patNames, height=16, width = 30, selectmode='single', exportselection=False)
patList.grid()

def get_pattern_name(event):
    global patternSelected
    global patternDict
    index = patList.curselection()[0]
    patternSelected = patternList[index]
    patternDict = setvar_dict(patterns[patternSelected])#(patternParDict[preset])
    print(patternSelected)
    updatePatternParameters()
    updatePrinterParameters()

patList.bind("<ButtonRelease-1>", get_pattern_name)



# =============================
# PRINTER SELECT LISTBOX
# =============================
printerNames = ()
for x in printersParDict:
    printerNames += (x,)
printerNames = tuple(sorted(printerNames))
print(printerNames)
prinNames = tk.StringVar(value=printerNames)

prinList = tk.Listbox(frame_printers, listvariable=prinNames, height=12, width = 30, selectmode='single', exportselection=False)
prinList.grid()

# select_printer(printerSelected)

def get_printer_name(event):
    global printerSelected
    global printerDict
    index = prinList.curselection()[0]
    printerSelected = printerNames[index]
    printerDict = setvar_printer_dict(printersParDict[printerSelected])
    print(printerSelected)
    updatePrinterParameters()
    updatePatternParameters()

prinList.bind("<ButtonRelease-1>", get_printer_name)



# BOUND ENTRY BOX TO INTEGERS
valint = (tk.Tk.register(root, validate_int), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
valflt = (tk.Tk.register(root, validate_float), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')



# =============================
# SET PATTERN PARAMETERS FRAME
# =============================
patternDict = setvar_dict(patterns[patternSelected])
drop_size = tk.IntVar()
drop_size.set(1)
filename_var = tk.StringVar()
filename_var.set(slugify(patternSelected))

def updatePatternParameters():
    for child in frame_patterns_par.winfo_children():
        child.destroy()
    global curRow
    curRow = 0


    patternDict = setvar_dict(patterns[patternSelected])
    filename_var.set(slugify(patternSelected))

    frame_patterns_par.grid_columnconfigure(0, minsize=150)
    frame_patterns_par.grid_columnconfigure(2, minsize=200)
    frame_patterns_par.grid_columnconfigure(3, minsize=120)

    ttk.Label(frame_patterns_par, text='Basic Options', font=('sansseriv', 12)).grid(row=nR(), column=0)
    addEntry(frame_patterns_par, 'X position', 'microns', patternDict['posx'][1], nR(), valcmd=valflt) if patterns[patternSelected]['posx'][0] else None
    addEntry(frame_patterns_par, 'Y position', 'cm', patternDict['posy'][1], nR(), valcmd=valflt) if patterns[patternSelected]['posy'][0] else None
    addEntry(frame_patterns_par, 'Distance dx', u'\u03bcm', patternDict['dx'][1], nR(), valcmd=valflt) if patterns[patternSelected]['dx'][0] else None

    # addEntry(frame_patterns_par, 'Distance dy', u'nozzle stretch (0 = 211.67 \u03bcm)', patternDict['dy'][1], nR(), valcmd=valint) if patterns[patternSelected]['dy'][0] else None
    if patterns[patternSelected]['dy'][0]:
        updateDyVar()
        ttk.Label(frame_patterns_par, text='Distance dy: ').grid(row=nR(), column=0, sticky="e", pady=2)
        tk.Spinbox(frame_patterns_par, from_=0, to=29, textvariable=patternDict['dy'][1], width=11, command=updateDyVar, validate='key', validatecommand=valint).grid(row=sR(),column=1, pady=2, padx=5, sticky="e")
        ttk.Label(frame_patterns_par, textvariable=dy_var).grid(row=sR(), column=2, sticky="w", pady=2)

    addEntry(frame_patterns_par, 'Raster width', 'dots', patternDict['widthn'][1], nR(), valcmd=valint) if patterns[patternSelected]['widthn'][0] else None
    addEntry(frame_patterns_par, 'Raster height', 'dots', patternDict['heightm'][1], nR(), valcmd=valint) if patterns[patternSelected]['heightm'][0] else None
    addEntry(frame_patterns_par, 'Distance between patterns', u'\u03bcm', patternDict['rdx'][1], nR(), valcmd=valflt) if patterns[patternSelected]['rdx'][0] else None

    ttk.Label(frame_patterns_par, text='Droplet size: ').grid(row=nR(), column=0, sticky="se", pady=(20, 2)) if patterns[patternSelected]['dropsize'][0] else None
    ttk.Radiobutton(frame_patterns_par, text='Small', variable=drop_size, value=1).grid(row=sR(), column=1, columnspan=2, sticky='sw', padx=3) if patterns[patternSelected]['dropsize'][0] else None
    ttk.Radiobutton(frame_patterns_par, text='Medium', variable=drop_size, value=2).grid(row=nR(), column=1, columnspan=2, sticky='w', padx=3) if patterns[patternSelected]['dropsize'][0] else None
    ttk.Radiobutton(frame_patterns_par, text='Large', variable=drop_size, value=3).grid(row=nR(), column=1, columnspan=2, sticky='w', padx=3) if patterns[patternSelected]['dropsize'][0] else None

    # advanced options....
    curRow=0
    frame_patterns_par.grid_columnconfigure(2, minsize=200)
    ttk.Label(frame_patterns_par, text='Advanced Options', font=('sansseriv', 12)).grid(row=nR(), column=3, columnspan=2, sticky="w")
    addEntry(frame_patterns_par, 'Repetitions', 'dots over each other', patternDict['rep'][1], nR(), 3, valcmd=valint) if patterns[patternSelected]['rep'][0] else None
    addEntry(frame_patterns_par, 'First active nozzle', 'nozzle', patternDict['fan'][1], nR(), 3, valcmd=valint) if patterns[patternSelected]['fan'][0] else None
    addEntry(frame_patterns_par, 'Width scaling', '(3 gives equal horizontal and vertical stretch)', patternDict['stretch'][1], nR(), 3, valcmd=valint) if patterns[patternSelected]['stretch'][0] else None

    if patternSelected == 'Load Bitmap':
        ttk.Label(frame_patterns_par, text=' ').grid(row=nR())
        ttk.Button(frame_patterns_par, text='TestButton', command=load_bitmap1).grid(row=nR(), column=1)

updatePatternParameters()




# =============================
# SET PRINTER PARAMETERS FRAME
# =============================
printerDict = setvar_printer_dict(printersParDict[printerSelected])
unibimode = tk.IntVar()
unibimode.set(1)
colorSelection = tk.StringVar()
colorSelection.set('magenta')



def updatePrinterParameters():
    for child in frame_printers_par.winfo_children():
        child.destroy()
    global curRow
    curRow = 0

    frame_printers_par.grid_columnconfigure(0, minsize=150)
    frame_printers_par.grid_columnconfigure(2, minsize=200)
    frame_printers_par.grid_columnconfigure(3, minsize=120)

    ttk.Label(frame_printers_par, text='Basic Options', font=('sansseriv', 12)).grid(row=nR(), column=0)
    addEntry(frame_printers_par, 'Page Management', '', printerDict['pmgmt'], nR(), valcmd=valint)
    addEntry(frame_printers_par, 'Vertical Unit', '', printerDict['vert'], nR(), valcmd=valint)
    addEntry(frame_printers_par, 'Horizontal Unit', '', printerDict['hor'], nR(), valcmd=valint)
    addEntry(frame_printers_par, 'Nozzles', '', printerDict['nozzles'], nR(), valcmd=valint)
    addOption(frame_printers_par, 'Nozzle Row', colorSelection, colorNames, nR()) if patterns[patternSelected]['color'] else None


    ttk.Label(frame_printers_par, text='Print Direction Method ').grid(row=nR(), column=0, sticky="se")
    ttk.Radiobutton(frame_printers_par, text='Unidirectional', variable=unibimode, value=1).grid(row=sR(), column=1, columnspan=2, sticky='sw', padx=3)
    ttk.Radiobutton(frame_printers_par, text='Bidirectional', variable=unibimode, value=0).grid(row=nR(), column=1, columnspan=2, sticky='w', padx=3)

    # advanced options....
    curRow=0
    frame_printers_par.grid_columnconfigure(2, minsize=200)
    ttk.Label(frame_printers_par, text='Advanced Options', font=('sansseriv', 12)).grid(row=nR(), column=3, columnspan=2, sticky="w")
    # addEntry(frame_printers_par, 'First active nozzle', 'nozzle', printerDict['pmid'], nR(), 3, valcmd=valint)
    addOption(frame_printers_par, 'Dot quality', printerDict['d'], dotNames, nR(), 3)
    addOption(frame_printers_par, 'Mod Unit', printerDict['m'], modUnits, nR(), 3, valcmd=valint)
    addOption(frame_printers_par, 'Print Method ID', printerDict['pmid'], pmidNames, nR(), 3)


updatePrinterParameters()




# =============================
# CONTROL FRAME
# =============================
current_dir = os.path.dirname(os.path.realpath(__file__))
save_dir_var = tk.StringVar()
save_dir_var.set(current_dir+'/output')
lpname_var = tk.StringVar()
#lpname_var.set("xp235-ink-new") 
#lpname_var.set("Epson_Stylus_SX235") #printer rechts
lpname_var.set("Epson-XP-235") #printer links

ParseOpt = [("None", "None"), ("Desc", "v"), ("Decomp", "V"), ("Hex", "ghex")]
ParseOpt_var = tk.StringVar()
ParseOpt_var.set("None")




def get_values(event=None):
    global x, y, dx, dy, rdx, n, m, size, fan, rep, stretch
    global pmgmt, vert, hor, mm, nozzles, d, pmid, umode
    global black, black2, black3, yellow, magenta, cyan, color
    global prnname, linux_name

    x = patternDict['posx'][1].get()/(2.54*10000) if patternDict['posx'][0] else 5
    y = patternDict['posy'][1].get()/2.54 if patternDict['posy'][0] else 3
    dx = um_in(patternDict['dx'][1].get()) if patternDict['dx'][0] else um_in(250)
    dy = patternDict['dy'][1].get() if patternDict['dy'][0] else 0
    rdx = um_in(patternDict['rdx'][1].get()) if patternDict['rdx'][0] else um_in(5000)
    n = patternDict['widthn'][1].get() if patternDict['widthn'][0] else 1
    m = patternDict['heightm'][1].get() if patternDict['heightm'][0] else 1
    size = drop_size.get() if patternDict['dropsize'][0] else 1
    fan = patternDict['fan'][1].get() if patternDict['fan'][0] else 0
    rep = patternDict['rep'][1].get() if patternDict['rep'][0] else 1
    stretch = patternDict['stretch'][1].get() if patternDict['stretch'][0] else 0

    pmgmt = printerDict['pmgmt'].get()
    vert = printerDict['vert'].get()
    hor = printerDict['hor'].get()
    mm = printerDict['m'].get()
    nozzles = printerDict['nozzles'].get()
    d = dotOpt[printerDict['d'].get()]
    pmid = pmidOpt[printerDict['pmid'].get()]
    prnname = printerDict['prnfiles'].get()
    linux_name = printerDict['linux-name'].get()

    umode = unibimode.get()
    if umode == 1:
        umode = b'\x01'
    elif umode == 0:
        umode = b'\x00'

    try:
        color = printerDict[colorSelection.get()]
    except:
        tk.messagebox.showerror('Color Error', "Selected color is not properly setup for this printer, try default color 'black'.")

    try:
        black = printerDict['black']
        black3 = printerDict['black3']
        black2 = printerDict['black2']
        cyan = printerDict['cyan']
        yellow = printerDict['yellow']
        magenta = printerDict['magenta']
    except:
        tk.messagebox.showerror("Color Error", "Selected color is (maybe) not set up, try default color 'black'. ")

    print("Values geGet")


def run_program(event=None):
    global rasterdata, body, header, footer, totaldata

    get_values()

    #x = x + x_d_overlap

    #interx() #location of interx calling

    header = load_prn_file('prns/' + prnname + '/' + prnname + '-header.prn')
    footer = load_prn_file('prns/' + prnname + '/' + prnname + '-footer.prn')

    body = ESC_Graph() + ESC_Units(pmgmt, vert, hor, mm) + ESC_Kmode() + \
           ESC_imode() + ESC_Umode(umode) + ESC_edot(d) + ESC_Dras() + \
           ESC_C(pmgmt) + ESC_c(pmgmt) + ESC_S(pmgmt) + ESC_m(pmid)


    try:
        rasterdata = patternDict['command'][0]()#(n=n,m=m,size=size,dx=dx,dy=dy,fan=fan,rep=rep, stretch=stretch, rdx=rdx, x=x, y=y, hor=hor, vert=vert, pmgmt=pmgmt, nozzles=nozzles)
        
        #check if rasterdata is defined
        try:
            rasterdata
        except NameError:
            print("Well, rasterdata WASN'T defined after all!")

        totaldata = header + body + rasterdata + footer
    except:
        tk.messagebox.showerror("ESC Command Error", "Command for this pattern could not be generated.\nSelected color probably not properly setup for this printer.")

    #tk.messagebox.showinfo("Data Generated", "The required ESC Commands are generated!")
    print("The required ESC Commands are generated!")



get_values()
print("Init get_values()")











def set_save_dir(event=None):
    # global save_dir
    save_dir = filedialog.askdirectory()
    save_dir_var.set(save_dir)
    print(save_dir)


def reset_vars(event=None):
    drop_size.set(1)
    unibimode.set(1)
    colorSelection.set('black')
    save_dir_var.set(current_dir+'/output')
    filename_var.set(slugify(patternSelected))
    load_patterns()
    updatePatternParameters()
    updatePrinterParameters()
    tk.messagebox.showinfo("Parameters Reset", "All parameters were Reset!")


def save_temp():
    global path
    run_program()
    path = save_dir_var.get()+'/temp.prn'
    save_prn_file(input=totaldata, filename='temp', folder=save_dir_var.get())


def save_output_file(event=None):
    run_program()
    filename=filename_var.get()
    save_prn_file(input=totaldata ,filename=filename, folder=save_dir_var.get())
    tk.messagebox.showinfo("Output Saved", "Save Successful")


# def set_plname():


def print_esc_commands(event=None, PLNAME='def'):
    global n_steps_n
    
    for n_steps_n in range(n_steps_round):
        enableArduino=1 #int(input("Enable Arduino? 1: yes, 0: no \n"))
        if enableArduino == 1:
            arduinoLoop() #let y-platform go to right direction before calling the print
        
        if PLNAME == 'def':
            plname = lpname_var.get()
        else:
            plname = simpledialog.askstring("Set Printer Name", "Linux printer name:", initialvalue=lpname_var.get())
            lpname_var.set(plname)
        # linux_command = "lp -d "+printersParDict[printerSelected]['linux-name']+" -oraw "+path
        save_temp()
        try:
            subprocess.call(["lp", "-d", plname, "-oraw", path])
            sleepTime(timeToPrint, "printing")
            print("\n")
            # Abel call function to see if printer is done
        except:
            tk.messagebox.showerror("Linux Error", "Could not print the data due to a error in Linux, the printername is probably not setup correctly.")



def cancel_print_jobs(event=None):
    subprocess.call(["cancel", "-a"])
    tk.messagebox.showinfo("Print Jobs Canceled", "Success")


# def restart_cups(event=None):
#     os.system("sudo /etc/init.d/cups restart")


def parse_escp2(event=None):
    save_temp()
    option = ParseOpt_var.get()
    if option == "ghex":
        os.system("ghex "+path)
    else:
        if option == "None":
            popt=""
        elif option == "V":
            popt="-V "
        elif option == "v":
            popt="-v "
        else:
            popt=""

        os.system("perl "+current_dir+"/gutenprint/parse-escp2 "+popt+path+" > "+current_dir+"/output/parse.txt")
        os.system("xdg-open "+current_dir+"/output/parse.txt")
    # print(subprocess.check_output(["perl", "~/bep/gutenprint5/test/parse-escp2", path]))


def unprint_escp2(event=None):
    save_temp()
    os.system("~/gutenprint/test/unprint " + path + " " + current_dir+"/output/temp.pnm")
    os.system("xdg-open " + current_dir+"/output/temp.pnm")
    # print(subprocess.check_output(["~/bep/gutenprint5/test/unprint", path]))


def open_help_pdf(event=None):
    nsy()







GetButton = ttk.Button(frame_controls, text='Get Data')
GetButton.bind("<ButtonRelease-1>", get_values)

GenerateButton = ttk.Button(frame_controls, text='Generate')
GenerateButton.bind("<ButtonRelease-1>", run_program)

SaveDirButton = ttk.Button(frame_controls, text="Browse...")
SaveDirButton.bind("<ButtonRelease-1>", set_save_dir)

SaveDirEntry = ttk.Entry(frame_controls, textvariable=save_dir_var, width=50)

FilenameEntry = ttk.Entry(frame_controls, textvariable=filename_var, width=50)

ResetButton = ttk.Button(frame_controls, text="Reset")
ResetButton.bind("<ButtonRelease-1>", reset_vars)

SaveFileButton = ttk.Button(frame_controls, text='Save File')
SaveFileButton.bind("<ButtonRelease-1>", save_output_file)

FolderLabel = ttk.Label(frame_controls, text="Folder: ")
FilenameLabel = ttk.Label(frame_controls, text="Filename: ")

LinuxLabel = ttk.Label(frame_controls, text="Linux Only:", font=LARGE_FONT)

PrintButton = ttk.Button(frame_controls, text="Print Data")
PrintButton.bind("<ButtonRelease-1>", print_esc_commands)

LinuxPrinterNameLabel = ttk.Label(frame_controls, text="Linux Printer name: ")
LinuxPrinterNameEntry = ttk.Entry(frame_controls, textvariable=lpname_var)

ParseButton = ttk.Button(frame_controls ,text="Parse ESCP2")
ParseButton.bind("<ButtonRelease-1>", parse_escp2)

UnprintButton = ttk.Button(frame_controls, text="Unprint")
UnprintButton.bind("<ButtonRelease-1>", unprint_escp2)

ResetButton.grid(row=0, column=0, pady=2, padx=10)
GetButton.grid(row=1, column=0, pady=2, padx=10)
GenerateButton.grid(row=2, column=0, pady=2, padx=10)

FolderLabel.grid(row=0, column=1, pady=2, sticky="e")
SaveDirEntry.grid(row=0, column=2, pady=2)
SaveDirButton.grid(row=0, column=3, pady=2, padx=(10,0))
FilenameLabel.grid(row=1, column=1, pady=2, sticky="e")
FilenameEntry.grid(row=1, column=2, pady=2)
SaveFileButton.grid(row=1, column=3, pady=2, padx=(10,0))

LinuxLabel.grid(row=0, column=4, pady=2, padx=(100,30))
PrintButton.grid(row=0, column=5, pady=2, padx=(0,25), sticky="w")
ParseButton.grid(row=1, column=5, sticky="w")
UnprintButton.grid(row=2, column=5, sticky="w")

LinuxPrinterNameLabel.grid(row=0, column=6, sticky="e")
LinuxPrinterNameEntry.grid(row=0, column=7)

# Parse options:
ParseFrame = ttk.Frame(frame_controls)
for Ptext, Pmode in ParseOpt:
    ParseRadiobuttons = ttk.Radiobutton(ParseFrame, text=Ptext, variable=ParseOpt_var, value=Pmode)
    ParseRadiobuttons.pack(side="left")
ParseFrame.grid(row=1, column=6, columnspan=2, sticky="w")

print("End initial code")

root.resizable(0,0)
root.mainloop()



"""
TODO:

Make a loop to print multiple rasters after each other to interlace




"""