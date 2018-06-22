## ==== IMPORT MODULES ====
import binascii
from DoD.hex_functions import *


## ==================================================================================================
## ==========================    CREATE BODY FUNCTIONS    ===========================================
## ==================================================================================================



## SELECT GRAPHICS MODE: ESC ( G
def ESC_Graph():
    prefix = b'\x1b' + str_hex('(G')  # ESC ( G
    nL = b'\x01'
    nH = b'\x00'
    m = b'\x01'
    total = prefix + nL + nH + m
    return total


# end ESC G



## SET UNITS: ESC ( U
def ESC_Units(pmgmt=720, vert=720, hor=5760, m=5760):
    """ESC_Units(m,res)
    m is max 5760
    res is max 2880, default is 720"""
    prefix = b'\x1b' + str_hex('(U')  # ESC ( U
    if m % 90 != 0:
        print("ERROR, m not in range {90, 120, 180, 360, 720, 1440, 2880, 5760}")
    else:
        nL = b'\x05'
        nH = b'\x00'
        P = dec_hex(m / pmgmt)
        V = dec_hex(m / vert)
        H = dec_hex(m / hor)
        mL = dec_hex(m % 256)
        mH = dec_hex(m / 256)
        total = prefix + nL + nH + P + V + H + mL + mH
        # print(total)
        return total


# end ESC ( U



## MONOCHROME MODE: ESC ( K
def ESC_Kmode(n=b'\x02'):
    prefix = b'\x1b' + str_hex('(K')  # ESC ( K
    nL = b'\x02'  # MANUAL SAYS 01H, output gives 02H
    nH = b'\x00'
    m = b'\x00'
    total = prefix + nL + nH + m + n
    return total


# end ESC ( K



## MICROWEAVE MODE: ESC ( i
def ESC_imode(n=b'\x01'):
    prefix = b'\x1b' + str_hex('(i') + b'\x01\x00'  # ESC ( i
    n = n
    total = prefix + n
    return total


# end ESC ( i



## UNIDIRECTIONAL MODE: ESC U
def ESC_Umode(n=b'\x00'):
    prefix = b'\x1b' + str_hex('U')  # ESC U
    n = n
    total = prefix + n
    return total


# end ESC U



## SELECT DOT SIZE: ESC ( e
def ESC_edot(d=b'\x12'):
    prefix = b'\x1b' + str_hex('(e')  # ESC ( e
    nL = b'\x02'
    nH = b'\x00'
    m = b'\x00'
    d = d
    total = prefix + nL + nH + m + d
    return total


# end ESC ( e



## SET RASTER IMAGE RESOLUTION: ESC ( D
def ESC_Dras(v=120, h=40):
    prefix = b'\x1b' + str_hex('(D')  # ESC ( D
    nL = b'\x04'
    nH = b'\x00'
    rL = b'\x40'
    rH = b'\x38'
    v = dec_hex(v)
    h = dec_hex(h)
    total = prefix + nL + nH + rL + rH + v + h
    return total


# finish meaning rL & rH etc.
# end ESC ( D



## SET PAGE LENGTH: ESC ( C
def ESC_C(pmgmt, m=8660 / 720):
    prefix = b'\x1b' + str_hex('(C')  # ESC ( C
    nL = b'\x04'  # number of bytes to follow
    nH = b'\x00'
    m = m * pmgmt
    m1 = dec_hex(int(round((m % 256))))
    m2 = dec_hex(int(m / 256))
    m3 = dec_hex(int(m / 256 / 256))
    m4 = dec_hex(int(m / 256 / 256 / 256))
    # print('vloc: %s %s %s %s' % (m1, m2, m3, m4))
    total = prefix + nL + nH + m1 + m2 + m3 + m4
    return total


# end ESC ( C

## SET PAGE FORMAT: ESC ( c
def ESC_c(pmgmt, t=0, b=8340 / 720):
    prefix = b'\x1b' + str_hex('(c')  # ESC ( c
    nL = b'\x08'  # number of bytes to follow
    nH = b'\x00'
    t = t * pmgmt
    b = b * pmgmt
    t1 = dec_hex(int(round((t % 256))))
    t2 = dec_hex(int(t / 256))
    t3 = dec_hex(int(t / 256 / 256))
    t4 = dec_hex(int(t / 256 / 256 / 256))
    b1 = dec_hex(int(round((b % 256))))
    b2 = dec_hex(int(b / 256))
    b3 = dec_hex(int(b / 256 / 256))
    b4 = dec_hex(int(b / 256 / 256 / 256))

    total = prefix + nL + nH + t1 + t2 + t3 + t4 + b1 + b2 + b3 + b4
    return total


# end ESC ( c


## SET PAPER DIMENSIONS: ESC ( S
def ESC_S(pmgmt, w=5950 / 720, l=8660 / 720):
    prefix = b'\x1b' + str_hex('(S')  # ESC ( S
    nL = b'\x08'  # number of bytes to follow
    nH = b'\x00'
    w = w * pmgmt
    l = l * pmgmt
    w1 = dec_hex(int(round((w % 256))))
    w2 = dec_hex(int(w / 256))
    w3 = dec_hex(int(w / 256 / 256))
    w4 = dec_hex(int(w / 256 / 256 / 256))
    l1 = dec_hex(int(round((l % 256))))
    l2 = dec_hex(int(l / 256))
    l3 = dec_hex(int(l / 256 / 256))
    l4 = dec_hex(int(l / 256 / 256 / 256))

    total = prefix + nL + nH + w1 + w2 + w3 + w4 + l1 + l2 + l3 + l4
    return total


# end ESC ( S



## SET PRINT MENTOD ID: ESC ( m
def ESC_m(m=b'\x21'):
    if m == b'':
        total = b''
    else:
        prefix = b'\x1b' + str_hex('(m')
        nL = b'\x01'
        nH = b'\x00'
        # m = b'\x21'
        total = prefix + nL + nH + m
    return total


# end ESC G



## ===============================================
## ===============================================
## ===============================================




## SET RELATIVE VERTICAL POSITION:
def ESC_v(vert, m=0):
    prefix = b'\x1b' + str_hex('(v')  # ESC ( v
    nL = b'\x04'  # number of bytes to follow
    nH = b'\x00'
    m = m * vert
    m1 = dec_hex(int(round((m % 256))))
    m2 = dec_hex(int(m / 256))
    m3 = dec_hex(int(m / 256 / 256))
    m4 = dec_hex(int(m / 256 / 256 / 256))
    # print('vloc: %s %s %s %s' % (m1, m2, m3, m4))
    total = prefix + nL + nH + m1 + m2 + m3 + m4
    return total


# end ESC ( v



## SET ABSOLUTE VERTICAL POSITION:
def ESC_V(vert, m=0):
    prefix = b'\x1b' + str_hex('(V')  # ESC ( V
    nL = b'\x04'  # number of bytes to follow
    nH = b'\x00'
    m = m * vert
    m1 = dec_hex(int(round((m % 256))))
    m2 = dec_hex(int(m / 256))
    m3 = dec_hex(int(m / 256 / 256))
    m4 = dec_hex(int(m / 256 / 256 / 256))
    # print('vloc abs: %s %s %s %s' % (m1, m2, m3, m4))
    total = prefix + nL + nH + m1 + m2 + m3 + m4
    return total


# end ESC ( V



## SET ABSOLUTE HORIZONTAL POSITION:
def ESC_dollar(hor, m=0):
    prefix = b'\x1b' + str_hex('($')  # ESC ( v
    nL = b'\x04'  # number of bytes to follow
    nH = b'\x00'
    m = m * hor
    m = int(m)
    m1 = dec_hex(int(round((m % 256))))
    m2 = dec_hex(int(m / 256))
    m3 = dec_hex(int(m / 256 / 256))
    m4 = dec_hex(int(m / 256 / 256 / 256))
    # print('hor loc: %s %s %s %s' % (m1, m2, m3, m4))
    total = prefix + nL + nH + m1 + m2 + m3 + m4
    return total


# end ESC ( $

## SET RELATIVE HORIZONTAL POSITION:
def ESC_slash(hor, m=0):
    prefix = b'\x1b\x28\x2f'  # ESC ( /
    nL = b'\x04'  # number of bytes to follow
    nH = b'\x00'
    m = m * hor
    m1 = dec_hex(int(round((m % 256))))
    m2 = dec_hex(int(m / 256))
    m3 = dec_hex(int(m / 256 / 256))
    m4 = dec_hex(int(m / 256 / 256 / 256))
    # print('hor loc: %s %s %s %s' % (m1, m2, m3, m4))
    total = prefix + nL + nH + m1 + m2 + m3 + m4
    return total


# end ESC ( /


## ===============================================
## ===============================================
## ===============================================
## ===============================================




## TRANSFER RASTER IMAGE: ESC i
def ESC_i(r=b'\x60', dots=1, n=722, m=30, an=1, size=3):
    prefix = b'\x1b' + str_hex('i')  # ESC i
    # r = bytearray.fromhex(str(r).zfill(2))
    c = b'\x01'
    b = b'\x02'
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    if dots == 1:
        if size == 3:
            aa = b'\x81\xff\x81\xff\x81\xff\x81\xff\x81\xff\xaf\xff'  # large
            # aa = b'\x81\xaa\x81\xaa\x81\xaa\x81\xaa\x81\xaa\xaf\xaa' # med
            # aa = b'\x81\x55\x81\x55\x81\x55\x81\x55\x81\x55\xaf\x55' # small
            bb = b'\x81\x00\x81\x00\x81\x00\x81\x00\x81\x00\xaf\x00'
            image = aa + 29 * bb  # XXX SPECIFIC FOR SX235W XXX
            # print(image)
    elif dots == 2:
        if size == 3:
            nL = b'\x00'
            nH = b'\x01'
            mL = b'\x80'
            mH = b'\x00'
            bb = b'\x81\xFF\x81\xFF'  # 2*4*128 dots is 1024
            image = bb * 128
            # print(image)
    elif dots == 3:
        if size == 3:
            aa = b'\x81\xff\x81\x00\x81\x00\x81\x00\x81\x00\xaf\x00'  # large
            # aa = b'\x81\xaa\x81\xaa\x81\xaa\x81\xaa\x81\xaa\xaf\xaa' # med
            # aa = b'\x81\x55\x81\x55\x81\x55\x81\x55\x81\x55\xaf\x55' # small
            bb = b'\x81\x00\x81\x00\x81\x00\x81\x00\x81\x00\xaf\x00'
            image = aa + 29 * bb  # XXX SPECIFIC FOR SX235W XXX
            # print(image)
    else:
        print('not yet supported number of dots')

    suffix1 = b'\x0d'
    total = prefix + r + c + b + nL + nH + mL + mH + image + suffix1
    return total


# end ESC i


## TRANSFER RASTER IMAGE: ESC i
def ESC_i_128(r=60, n=128, m=128, an=1, dots=1, size=1):
    prefix = b'\x1b' + str_hex('i')  # ESC i
    # r = bytearray.fromhex(str(r).zfill(2))
    c = b'\x01'
    b = b'\x02'
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    if dots == 1:
        if size == 3:
            aa = b'\x81\x03\x81\x03'
        elif size == 2:
            aa = b'\x81\x02\x81\x02'
        elif size == 1:
            aa = b'\x81\x01\x81\x01'
        image = aa * m
        # print(image)
    elif dots == 2:
        if size == 3:
            aa = b'\x81\x00\xa7\x00'
            bb = b'\x81\xff\xa7\xff'
        if size == 2:
            aa = b'\x81\x00\xa7\x00'
            bb = b'\x81\xaa\xa7\xaa'
        if size == 1:
            aa = b'\x81\x00\xa7\x00'
            bb = b'\x81\x55\xa7\x55'
            # print(image)
        image = m * bb
    elif dots == 3:
        # n = 3
        aa = b'\x00\x03\x00\x03\x00\x03'
        bb = b'\x00\x00\x00\x00\x00\x00'
        image = (an - 1) * bb + aa + (m - an) * bb
    elif dots == 4:
        # n = 3
        aa = b'\x00\x03\x00\x03\x00\x03\x00\x03'
        bb = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        image = (an - 1) * bb + aa + (m - an) * bb
    elif dots == 8:
        aa = b'\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x03'
        bb = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        image = (aa + bb + bb) * 8 + (m - 8 * 3) * bb

    else:
        print('not yet supported number of dots')

    suffix1 = b'\x0d'
    total = prefix + r + c + b + nL + nH + mL + mH + image + suffix1
    return total


# end ESC i




###

def ESC_i_matrix(color, matrix, spacing=3, size=1, fan=1):
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'
    b = b'\x02'
    r = color

    rasterbin = ''
    sp = spacing
    for i in range(len(matrix)):  # i vertical
        for j in range(len(matrix[0])):  # j horizontal
            if matrix[i][j] == 0:
                rasterbin += '00' + '00' * sp
            elif matrix[i][j] == 1:
                if size == 1:
                    rasterbin += '01' + '00' * sp
                elif size == 2:
                    rasterbin += '10' + '00' * sp
                elif size == 3:
                    rasterbin += '11' + '00' * sp
            elif matrix[i][j] == 2:
                rasterbin += '10' + '00' * sp
            elif matrix[i][j] == 3:
                rasterbin += '11' + '00' * sp
        if ((len(matrix[0]) * (1 + sp)) * 2) % 8 != 0:
            rasterbin += (8 - ((len(matrix[0]) * (1 + sp) * 2) % 8)) * '0'

    if ((len(matrix[0]) * (1 + sp)) * 2) % 8 != 0:
        n = ((len(matrix[0]) * (1 + sp) * 2) + (8 - ((len(matrix[0]) * (1 + sp) * 2) % 8))) / 8
    else:
        n = ((len(matrix[0]) * (1 + sp) * 2)) / 8

    print(rasterbin)

    raster = b''
    for i in range(0, len(rasterbin), 8):
        raster += b'\x00' + dec_hex(int(rasterbin[i:i + 8], 2))

    m = len(matrix)  # vertical raster size

    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    suffix1 = b'\x0d'
    total = prefix + r + c + b + nL + nH + mL + mH + raster + suffix1
    return total


# end ESC i

###



def ESC_i_1dot(r=b'\x60', m=128, an=1, size=1):
    prefix = b'\x1b' + str_hex('i')  # ESC i
    # r = bytearray.fromhex(str(r).zfill(2))
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    if size == 1:
        hd = b'\x01'  # b'\x40'
    elif size == 2:
        hd = b'\x02'  # b'\x80'
    elif size == 3:
        hd = b'\x03'  # b'\xc0'
    else:
        print('not supported dot size')

    rowd = b'\x00' + hd
    rowe = b'\x00\x00'
    image = (an - 1) * rowe + rowd + (m - an) * rowe
    suffix1 = b'\x0d'  # b'\x0d\x0c'
    total = prefix + r + c + b + nL + nH + mL + mH + image + suffix1
    return total


# end



def ESC_i_nrs(nozzlelist, r=b'\x00', size=1):
    """
    Input
    ============
    nozzlelist:    list containing 0 and 1 activating the specified nozzles
    r:             choose nozzle row (color), black cyan magenta yellow
    size:        size of the drops created
    """
    m = len(nozzlelist)
    prefix = b'\x1b' + str_hex('i')  # ESC i
    c = b'\x01'  # COMPRESSED
    b = b'\x02'
    n = 1
    nL = dec_hex(n % 256)
    nH = dec_hex(n / 256)
    mL = dec_hex(m % 256)
    mH = dec_hex(m / 256)

    if size == 1:
        hd = b'\x01'  # b'\x40'
    elif size == 2:
        hd = b'\x02'  # b'\x80'
    elif size == 3:
        hd = b'\x03'  # b'\xc0'
    else:
        print('not supported dot size')

    rowd = b'\x00' + hd
    rowe = b'\x00\x00' # Abel empty dots: doesnt print
    image = b''
    for x in nozzlelist:
        if x == 1:
            image += rowd
        elif x == 0:
            image += rowe
        else:
            print('Error, nozzlelist not correct format')

    # image = (an-1)*rowe+ rowd + (m-an)*rowe
    suffix1 = b'\x0d'  # b'\x0d\x0c'
    total = prefix + r + c + b + nL + nH + mL + mH + image + suffix1
    return total

# end
