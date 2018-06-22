## ==== IMPORT SCRIPTS ====
import binascii
from hex_functions import *
from esc_functions import *
from characters import *
import math


## ====================================================
## ==== SET IMAGE LOCATION AND HORIZONTAL SPACING =====
## ====================================================

x = 6
y = 2
# begin glass, x = 5 inch (4.5 now 29-11) last 4.6
# end glass x = 7.25 inch




## RASTER SPACING AND SIZE
nan = 5		# number of active nozzles
fan = 0		# first active nozzle
dy = 1		# spacing between nozzles (1 = 1 nozzle in between)
dx = (dy+1)*(1/120) 	# hor spacing, same as vert spacing using nozzle distance (manual)

## ==== active nozzle for single dot ====
an = 1





## ==== UNI/BI-DIRECTIONAL MODE PRINTHEAD =====
unim = b'\x01' # 01 uni, 00 bis



## ==== OUTPUT FOLDER ====
outputfolder = 'output'

## ====================================================
## ====================================================





## ==== DEFINE PRINTERS AND IMAGES ====
prn = ['sx235w', 'sx600fw', 'rx520', 'dx6050']


img = ['single-small', 'single-medium', 'single-large', 'raster-5x5-small', 'raster-5x5-med', \
'raster-5x5-big', 'allcolors', 'XXX', 'raster-nxm-custom', 'repeat-10-drops', 'n-small-med-large', \
'XXX', 'increasing-distance', 'repeat-10-1-drops', 'fill-glass', 'small-med-large-esci', \
'PME-logo-s', 'PME-logo-l', 'PME-NME', '3drops-esci', '4drops-esci', 'TUPME', \
'tudelft-logo', '8x8-10drops-esci', 'raster-20x20-small-med-large', \
'raster-90x90-black', '100d-20d', '40d-20d-water', '20x20-sml-5t-ls', 'tulogofast', 'P']

nprn = range(0,len(prn))
nimg = range(0,len(img))

	# 0:   1-small
	# 1:   1-medium
	# 2:   1-large
	# 3:   5x5-small
	# 4:   5x5-med
	# 5:   5x5-big
	# 6:   allcolors
	# 7:   testloc
	# 8:   nxm-spac
	# 9:   10-big
	# 10:   n-sml
	# 11:   n-sl
	# 12:   increasing-distance
	# 13:   10-1-big
	# 14:   full-dots
	# 15:   sml-esci
	# 16:   PME-logo-s
	# 17:   PME-logo-l
	# 18:   PME-NME
	# 19:   3drop
	# 20:   4drop
	# 21:   TUPME
	# 22:   LOGO
	# 23:   8x8-10drops
	# 24:   20x20-sml
	# 25:   90x90-black
	# 26:   100d-20d
	# 27:   40d-20d-water
	# 28:   20x20-sml-5t-ls
	# 29:	P


## ==== SELECT PRINTER AND LOAD PRINTER PARAMETERS ====
print('Available printers:')
for ka in nprn:
	print('   '+str(nprn[ka]) + ':   ' + prn[ka])
print()
np = int(input('select number of printer: '))
printer = prn[np]



# LOAD HEADER AND FOOTER FOR SELECTED PRINTER
header = load_prn_file('prns/'+printer+'/'+printer+'-header.prn')
footer = load_prn_file('prns/'+printer+'/'+printer+'-footer.prn')


# LOAD PARAMETERS FOR SELECTED PRINTER
if printer == 'sx600fw':
	# unit parameters
	pmgmt = 720
	vert = 720
	hor = 5760
	m = 5760
	nozzles = 128
	# select nozzle row (def black = 00)
	r = b'\x60'
	black = r
	# select dot size
	d = b'\x12'
	# set page method ID
	esc_m = ESC_m()
	
elif printer == 'sx235w':
	# unit parameters
	pmgmt = 720
	vert = 720
	hor = 5760
	m = 5760
	nozzles = 29
	# set nozzle row numbers (def black = 00)
	r = b'\x00'
	magenta = b'\x01'
	cyan = b'\x02'
	yellow = b'\x04'
	black = b'\x00'
	black2 = b'\x05'
	black3 = b'\x06'
	# select dot size
	d = b'\x11'
	# set page method ID
	esc_m = ESC_m(b'\x20')
	
elif printer == 'rx520':
	# unit parameters
	pmgmt = 720
	vert = 720
	hor = 720
	m = 2880
	nozzles = 90
	# select nozzle row (def black = 00)
	r = b'\x00'
	black = r
	# select dot sizes
	d = b'\x10'
	# set page method ID
	esc_m = b''
	
elif printer == 'dx6050':
	# unit parameters
	pmgmt = 720
	vert = 720
	hor = 720
	m = 2880
	nozzles = 90
	# select nozzle row (def black = 00)
	r = b'\x00'
	black = r
	# select dot sizes
	d = b'\x10'
	# set page method ID
	esc_m = b''
	
	
	"""
	ADD NEW PRINTER HERE!
	(elif printer == '<newprintername>')
	printer units can be found by parsing the prn file
	Same with color codes, print a file with all colors and parse it
	other specs can be found by looking in spec sheet or service manual (if available)
	"""
	
else:
	print('Not supported printer (yet)')
	print('Print a simple document using Gutenprint cups driver to a file printer and split the output using the data splitter')
# end printer parameter setup





## ==== SELECT IMAGE ====
print('Available images:')
for kb in nimg:
	print('   '+str(nimg[kb]) + ':   ' + img[kb])
print()
ni = int(input('select number of image: '))






print('===================================================')
print('   Selected image:  ' + img[ni])
print('   On printer:      ' + printer)
if unim == b'\x00':
	print('   Bidirectional')
elif unim == b'\x01':
	print('   Unidirectional')
print('===================================================')





## COMPOSE BODY
body = ESC_Graph() + ESC_Units(pmgmt,vert,hor,m) + ESC_Kmode() + \
ESC_imode() + ESC_Umode(unim) + ESC_edot(d) + ESC_Dras() + \
ESC_C(pmgmt) + ESC_c(pmgmt) + ESC_S(pmgmt) + esc_m




## CREATE IMAGE DATA WITH PREDETERMINED NOZZLE SPACING
if ni == 0:
	nozzlelist = createnozzlelist(29,1,0,an)
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,1) + b'\x0c'
elif ni == 1:
	nozzlelist = createnozzlelist(29,1,0,an)
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,2) + b'\x0c'
elif ni == 2:
	nozzlelist = createnozzlelist(29,1,0,an)
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,3) + b'\x0c'

elif ni == 3 or ni == 4 or ni == 5:
	if ni == 3:
		size = 1
	elif ni == 4:
		size = 2
	elif ni == 5:
		size = 3
	nozzlelist = createnozzlelist(29,5,dy)
	raster = b''
	for k in range(5):
		raster += ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,black,size)
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 6:
	nozzlelist = createnozzlelist(29,5,dy,1)
	size1 = 3
	size2 = 2
	size3 = 1
	x1 = x
	x2 = x1+0.5
	x3 = x2+0.5
	y = y
	raster1 = b''
	for k in range(5):
		raster1 += ESC_dollar(hor,(x1+dx*k)) + ESC_i_nrs(nozzlelist,black,size1) + \
		ESC_dollar(hor,(x1+dx*k)) + ESC_i_nrs(nozzlelist,black2,size1) + \
		ESC_dollar(hor,(x1+dx*k)) + ESC_i_nrs(nozzlelist,black3,size1) + \
		ESC_dollar(hor,(x1+(dx*6)+dx*k)) + ESC_i_nrs(nozzlelist,cyan,size1) + \
		ESC_dollar(hor,(x1+(dx*6)+dx*k)) + ESC_i_nrs(nozzlelist,magenta,size1) + \
		ESC_dollar(hor,(x1+(dx*6)+dx*k)) + ESC_i_nrs(nozzlelist,yellow,size1)
	raster2 = b''
	for k in range(5):
		raster2 += ESC_dollar(hor,x2+dx*k) + ESC_i_nrs(nozzlelist,black,size2) + \
		ESC_dollar(hor,x2+dx*k) + ESC_i_nrs(nozzlelist,black2,size2) + \
		ESC_dollar(hor,x2+dx*k) + ESC_i_nrs(nozzlelist,black3,size2) + \
		ESC_dollar(hor,x2+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,cyan,size2) + \
		ESC_dollar(hor,x2+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,magenta,size2) + \
		ESC_dollar(hor,x2+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,yellow,size2)
	raster3 = b''
	for k in range(5):
		raster3 += ESC_dollar(hor,x3+dx*k) + ESC_i_nrs(nozzlelist,black,size3) + \
		ESC_dollar(hor,x3+dx*k) + ESC_i_nrs(nozzlelist,black2,size3) + \
		ESC_dollar(hor,x3+dx*k) + ESC_i_nrs(nozzlelist,black3,size3) + \
		ESC_dollar(hor,x3+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,cyan,size3) + \
		ESC_dollar(hor,x3+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,magenta,size3) + \
		ESC_dollar(hor,x3+(dx*6)+dx*k) + ESC_i_nrs(nozzlelist,yellow,size3)
	rasterdata = ESC_v(pmgmt,y) + raster1 + raster2 + raster3 + b'\x0c'


elif ni == 7:
	nozzlelist = createnozzlelistsp(29,[0,1,2,3,25,26])
	size = 3
	raster = ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,size)
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 8:
	print()
	n = int(input('input grid number of dots horizontal: '))
	m = int(input('input grid number of dots vertical: '))
	size1 = int(input('size [1/2/3]: '))
	dx = int(input('input hor spacing in um: '))
	dx = um_in(dx)
	
	dy = int(input('input vert spacing in non active nozzles (nozzle spacing 1/120 inch = 211.66 um) (0 = separation of 1/120=211.66): '))
	# dx = 1/120
	nozzlelist = createnozzlelist(29,m,dy,1)
	raster1 = b''
	for k in range(n):
		raster1 += ESC_dollar(hor,(x+dx*k)) + ESC_i_nrs(nozzlelist,black,size1)
	
	rasterdata = ESC_v(pmgmt,y) + raster1 + b'\x0c'

elif ni == 9:
	nozzlelist = createnozzlelist(29,1,0,an)
	size1 = int(input('size [1/2/3]: '))
	raster = b''
	for k in range(10):
		raster += ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,size1)
	
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 10:
	n = int(input('Number of dots per dropsize: ')) # aantal druppels per dropsize
	x = 6
	dx = um_in(int(input('horizontal spacing in um: ')))
	dy = int(input('input vert spacing in non active nozzles (nozzle spacing 1/120 inch = 211.66 um) (0 = separation of 1/120=211.66): '))
	nozzlelist = createnozzlelist(30,n,dy,29)
	
	raster = ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,1) + \
	ESC_dollar(hor,x+dx) + ESC_i_nrs(nozzlelist,black,2) + \
	ESC_dollar(hor,x+2*dx) + ESC_i_nrs(nozzlelist,black,3) + \
	ESC_dollar(hor,x+0.25) + ESC_i_nrs(nozzlelist,black,1) + \
	ESC_dollar(hor,x+0.25+dx) + ESC_i_nrs(nozzlelist,black,2) + \
	ESC_dollar(hor,x+0.25+2*dx) + ESC_i_nrs(nozzlelist,black,3) + \
	ESC_dollar(hor,x+0.5) + ESC_i_nrs(nozzlelist,black,1) + \
	ESC_dollar(hor,x+0.5+dx) + ESC_i_nrs(nozzlelist,black,2) + \
	ESC_dollar(hor,x+0.5+2*dx) + ESC_i_nrs(nozzlelist,black,3)
	
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 11:
	n = int(input('Number of dots per dropsize: ')) # aantal druppels per dropsize
	dx = um_in(int(input('horizontal spacing in um: ')))
	dy = int(input('input vert spacing in non active nozzles (nozzle spacing 1/120 inch = 211.66 um) (0 = separation of 1/120=211.66): '))
	nozzlelist = createnozzlelist(29,n,dy,1)
	
	raster = ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,1) + \
	ESC_dollar(hor,x+2*dx) + ESC_i_nrs(nozzlelist,black,3)
	
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 12:
	nozzlelist1 = createnozzlelist(30,10,0,0)
	nozzlelist2 = createnozzlelist(30,10,0,10)
	nozzlelist3 = createnozzlelist(30,10,0,20)
	dxlist = [0,100,300,600,1000]
	size = int(input('size [1/2/3]: '))
	
	raster = b''
	for k in range(len(dxlist)):
		raster += ESC_dollar(hor,x+um_in(dxlist[k])) + ESC_i_nrs(nozzlelist1,black,size)
	
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 13:
	dy = 2
	dx = um_in(400)
	nozzlelist = createnozzlelist(29,3,dy,1)
	raster = b''
	size1 = int(input('size [1/2/3]: '))
	for k in range(10):
		raster += ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(9):
		raster += ESC_dollar(hor,x+dx) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(8):
		raster += ESC_dollar(hor,x+dx*2) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(7):
		raster += ESC_dollar(hor,x+dx*3) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(6):
		raster += ESC_dollar(hor,x+dx*4) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(5):
		raster += ESC_dollar(hor,x+dx*5) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(4):
		raster += ESC_dollar(hor,x+dx*6) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(3):
		raster += ESC_dollar(hor,x+dx*7) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(2):
		raster += ESC_dollar(hor,x+dx*8) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(1):
		raster += ESC_dollar(hor,x+dx*9) + ESC_i_nrs(nozzlelist,black,size1)
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'


elif ni == 14:
	dy = 1
	x = int(input('x start location (glass starts at approximately 4.77 inch)'))
	nozzles = 30
	times = int(input('number of dots (*23040, 10 => 230400): '))
	size1 = int(input('size [1/2/3]: '))
	# black = b'\x02'
	image = ESC_dollar(hor,x) + ESC_i_128(black,256,nozzles,0,1,size1) + ESC_dollar(hor,x) + ESC_i_128(b'\x05',256,nozzles,0,1,size1)+ESC_dollar(hor,x) + ESC_i_128(b'\x06',256,nozzles,0,1,size1)
	rasterdata = ESC_v(pmgmt,y) + image*times + b'\x0c'


elif ni == 15:
	dy = 1
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_128(black,3,nozzles,0,3) + b'\x0c'

elif ni == 16:
	dy = 0
	dx = (dy+1)*(1/120)
	
	rasterdata = ESC_v(pmgmt,y) + createPs(x) + createMs(x+4*dx) + createEs(x+8*dx) + b'\x0c'

elif ni == 17:
	dy = 0
	dx = (dy+1)*(1/120)
	
	rasterdata = ESC_v(pmgmt,y) + createP(x) + createM(x+6*dx) + createE(x+12*dx) + b'\x0c'

elif ni == 18:
	dy = 0
	dx = (dy+1)*(1/120)
	size1 = 3
	size2 = 1
	rasterdata = ESC_v(pmgmt,y) + createP(x,black,size1) + createM(x+6*dx,black,size1) + createE(x+12*dx,black,size1) + createM(x+dx*20,black,size2) + createN(x+26*dx,black,size2) + createE(x+32*dx,black,size2) + b'\x0c'

elif ni == 19:
	an = int(input('nozzle number: '))
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_128(black,3,nozzles,an,3,3) + b'\x0c'
elif ni == 20:
	an = int(input('nozzle number: '))
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_128(black,4,nozzles,an,4,3) + b'\x0c'

elif ni == 21:
	rasterdata = printTUPME(x)
elif ni == 22:
	matrix = loadlogo(2)
	size = int(input('size [1/2/3]: '))
	rasterdata = ESC_v(pmgmt,y) + printLOGO(matrix,x,y,size)
	# + printLOGO(matrix,x+0.8,y,2) + printLOGO(matrix,x+1.8,y,1) +  printLOGO(matrix,x,y,3,b'\x01') + printLOGO(matrix,x+0.8,y,2,b'\x01') + printLOGO(matrix,x+1.8,y,1,b'\x01') 
	rasterdata = rasterdata + b'\x0c'



elif ni == 23:
	# an = int(input('nozzle number: '))
	# size1 = int(input('size [1/2/3]: '))
	black2 = magenta
	black3 = yellow
	rasterdata = ESC_v(pmgmt,y) + \
	(ESC_dollar(hor,x) + ESC_i_128(black,16,nozzles,an,8,3))*10 + \
	(ESC_dollar(hor,x+0.5) + ESC_i_128(black,16,nozzles,an,8,3))*5 + \
	(ESC_dollar(hor,x+1) + ESC_i_128(black,16,nozzles,an,8,3))*1 + \
		(ESC_dollar(hor,x) + ESC_i_128(black2,16,nozzles,an,8,3))*10 + \
	(ESC_dollar(hor,x+0.5) + ESC_i_128(black2,16,nozzles,an,8,3))*5 + \
	(ESC_dollar(hor,x+1) + ESC_i_128(black2,16,nozzles,an,8,3))*1 + \
		(ESC_dollar(hor,x) + ESC_i_128(black3,16,nozzles,an,8,3))*10 + \
	(ESC_dollar(hor,x+0.5) + ESC_i_128(black3,16,nozzles,an,8,3))*5 + \
	(ESC_dollar(hor,x+1) + ESC_i_128(black3,16,nozzles,an,8,3))*1 + \
	b'\x0c'

elif ni == 24:
	nozzlelist = createnozzlelist(29,20,0,0)
	dx = 1/120
	raster1 = b''
	raster2 = b''
	raster3 = b''
	color = black
	for k in range(20):
		raster1 += ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,color,3)
		raster2 += ESC_dollar(hor,x+0.25+dx*k) + ESC_i_nrs(nozzlelist,color,2)
		raster3 += ESC_dollar(hor,x+0.5+dx*k) + ESC_i_nrs(nozzlelist,color,1)
	rasterdata = ESC_v(pmgmt,y)+raster1+raster2+raster3 + b'\x0c'

elif ni == 25:
	nozzlelist = createnozzlelist(30,30,0,0)
	dx = um_in(200)
	size = int(input('size [1/2/3]: '))
	raster1 = b''
	raster2 = b''
	raster3 = b''
	# color = black
	for k in range(90):
		raster1 += ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,black,size)
		raster2 += ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,black2,size)
		raster3 += ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,black3,size)
	rasterdata = ESC_v(pmgmt,y) + raster1+raster2+raster3 + b'\x0c'

elif ni == 26:
	nozzlelist = createnozzlelist(30,5,5,1)
	dx = um_in(2000)
	
	size1 = 3
	raster = b''
	for k in range(100):
		raster += ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(80):
		raster += ESC_dollar(hor,x+dx) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(60):
		raster += ESC_dollar(hor,x+dx*2) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(40):
		raster += ESC_dollar(hor,x+dx*3) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(20):
		raster += ESC_dollar(hor,x+dx*4) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(10):
		raster += ESC_dollar(hor,x+dx*4) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(5):
		raster += ESC_dollar(hor,x+dx*4) + ESC_i_nrs(nozzlelist,black,size1)
	for k in range(1):
		raster += ESC_dollar(hor,x+dx*4) + ESC_i_nrs(nozzlelist,black,size1)
	rasterdata = ESC_v(pmgmt,y) + raster + b'\x0c'

elif ni == 27:
	nozzlelist = createnozzlelist(30,5,5,1)
	dx = um_in(1000)
	size1 = 3
	raster = b''
	for k in range(40):
		raster += ESC_dollar(hor,x) + ESC_i_nrs(nozzlelist,black2,size1)
	for k in range(20):
		raster += ESC_dollar(hor,x+dx) + ESC_i_nrs(nozzlelist,black2,size1)
	rasterdata = raster + (ESC_dollar(hor,4.77) + ESC_i_128(cyan,256,nozzles,0,1,size1)+ ESC_dollar(hor,4.77) + ESC_i_128(yellow,256,nozzles,0,1,size1))*10

elif ni == 28:
	nozzlelist = createnozzlelist(29,10,1,0)
	dx = 2/120
	raster1 = b''
	raster2 = b''
	raster3 = b''
	color = black2
	for k in range(20):
		raster1 += (ESC_dollar(hor,x+dx*k) + ESC_i_nrs(nozzlelist,color,3))*5
		raster2 += (ESC_dollar(hor,x+0.4+dx*k) + ESC_i_nrs(nozzlelist,color,2))*5
		raster3 += (ESC_dollar(hor,x+0.8+dx*k) + ESC_i_nrs(nozzlelist,color,1))*5
	rasterdata = ESC_v(pmgmt,y)+raster1+raster2+raster3 + b'\x0c'
elif ni == 29:
	matrix = loadlogo(3)
	size = int(input('size [1/2/3]: '))
	rasterdata = ESC_v(pmgmt,y) + printLOGO(matrix,x,y,size)
	# + printLOGO(matrix,x+0.8,y,2) + printLOGO(matrix,x+1.8,y,1) +  printLOGO(matrix,x,y,3,b'\x01') + printLOGO(matrix,x+0.8,y,2,b'\x01') + printLOGO(matrix,x+1.8,y,1,b'\x01') 
	rasterdata = rasterdata + b'\x0c'

	##
elif ni == 30:
	rasterdata = ESC_v(pmgmt,y) + ESC_dollar(hor,x) + ESC_i_matrix(black,load_logo_fast(),0,3) + b'\x0c'



# print(rasterdata)





## COMBINE
total = header + body + rasterdata + footer

filename = outputfolder + '/' +printer + '_' + img[ni] + '.prn'
if not os.path.exists(outputfolder):
	os.makedirs(outputfolder)


## SAVE PRN FILE
save_prn_file(total,filename)
print('DONE!')
print('path: ' + filename)




