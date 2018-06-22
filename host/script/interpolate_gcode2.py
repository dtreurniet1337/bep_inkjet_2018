from math import *

def interpolate_gcode(file, stepsize):

    # Read and load file
    try:
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
    except Exception as e:
        return 'Error: '+str(e)

    # Collect corner points
    corners = []
    n_corners = 0
    new_segment = True
    for l in lines:
        # Ignore newlines
        if l.strip() == '': continue

        if l[0:2] == 'G1':
            if new_segment:
                corners.append([])
                new_segment = False
            try:
                # Determine X and Y declaration in Gcode
                x_index = l.index('X')
                y_index = l.index('Y')

                # Extract values after X and Y letters
                x = float(l[x_index+1: y_index].strip())
                y = float(l[y_index+1: -1].strip())

                # Store values in corner list
                corners[-1].append((x, y))
                n_corners += 1
                printing_segment = True
            except Exception as e:
                print('Failed to collect corners:\n%s'%(e))
        else:
            if corners != []: print(corners[-1])
            new_segment = True
    print("Found %s corners in %s segments"%(n_corners, len(corners)))

    # Create new file
    new_name = file[:-3]+'.interp.nc'
    f = open(new_name, 'w')

    # Go through corner list and generate interpolation steps




def get_dist(c1, c2):
    x2 = (c2[0] - c1[0])**2
    y2 = (c2[1] - c1[1])**2
    return sqrt(x2+y2)









    f.close()
    return new_name

def get_line(gcode_dict):
    string = ''
    string = string+' '+'G'+str(gcode_dict['G'])
    string = string+' '+'X'+str(gcode_dict['X'])
    string = string+' '+'Y'+str(gcode_dict['Y'])
    return string.strip()+'\n'


def get_gcode_parts(line):
    parts = line.split(' ')
    gcode_dict = {}
    for p in parts:
        gcode_dict[p[0]] = p[1:].strip()
    return gcode_dict
