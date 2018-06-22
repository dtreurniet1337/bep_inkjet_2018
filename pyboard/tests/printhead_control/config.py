

################## Pin definitions ###################

STEP_ENA =      'X8'

# X stage
X_DIR =         'X1'
X_STEP =        'X2'
X_END_MIN =     'X4'
X_END_MAX =     'X3'

# Y stage
Y_DIR =         'Y1'
Y_STEP =        'Y2'
Y_END_MIN =     'X12'
Y_END_MAX =     'X11'


# LV printhead logic
SICL =          'Y3'
SIBL =          'Y4'
CK =            'Y5'
LAT =           'Y6'
CH =            'Y7'
NCHG =          'Y8'

# GPIO addresses
GPIO_SICL =          8
GPIO_SIBL =          9
GPIO_CK =            12
GPIO_LAT =           13
GPIO_CH =            14
GPIO_NCHG =          15

# DAC
DAC =           'X5'


###################### MISC #########################

STAGE_MICROSTEPPING = 16
STAGE_RANGE = (100, 100) #mm
STAGE_PITCH = 1 #mm
STAGE_STEPS_PER_REV = 200
STAGE_STEP_DELAY = 500 #us


################## Settings ##########################
ENABLE_ENDSTOPS = False
