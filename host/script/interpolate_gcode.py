from math import *

def interpolate_gcode(file, stepsize):
    try:
        f = open(file, 'r')
        lines = f.readlines()
        f.close()
    except Exception as e:
        return 'Error: '+str(e)

    new_name = file[:-3]+'.interp.nc'
    f = open(new_name, 'w')

    droplet_counter = 0

    for i in range(len(lines)-1):
        if lines[i][:2] == 'G1' and lines[i+1][:2] == 'G1':
            dict1 = get_gcode_parts(lines[i])
            dict2 = get_gcode_parts(lines[i+1])

            delta_x = float(dict2['X']) - float(dict1['X'])
            delta_y = float(dict2['Y']) - float(dict1['Y'])

            vertical = horizontal = no_move = False
            if delta_x == 0 and delta_y != 0: vertical = True
            if delta_x != 0 and delta_y == 0: horizontal = True
            if delta_x == 0 and delta_y == 0: no_move = True


            f.write(lines[i])
            f.write('P1\n')
            if vertical:
                negative = False
                if delta_y < 0: negative = True
                for i in range(int((abs(delta_y)/(stepsize/1000)))):
                    new_dict = dict1.copy()
                    if not negative:
                        new_dict['Y'] = float(dict1['Y']) + (i+1)*(stepsize/1000)
                    else:
                        new_dict['Y'] = float(dict1['Y']) - (i+1)*(stepsize/1000)
                    f.write(get_line(new_dict))
                    f.write('P1\n')
                    droplet_counter += 1
            elif horizontal:
                negative = False
                if delta_x < 0: negative = True
                for i in range(int((abs(delta_x)/(stepsize/1000)))):
                    new_dict = dict1.copy()
                    if not negative:
                        new_dict['X'] = float(dict1['X']) + (i+1)*(stepsize/1000)
                    else:
                        new_dict['X'] = float(dict1['X']) - (i+1)*(stepsize/1000)
                    f.write(get_line(new_dict))
                    f.write('P1\n')
                    droplet_counter += 1
            elif no_move:
                pass
            else:
                alpha = atan(delta_y/delta_x)
                if delta_x<0: alpha += pi
                line_length = sqrt(delta_y**2 + delta_x**2)
                x_step = (stepsize/1000)*cos(alpha)
                y_step = (stepsize/1000)*sin(alpha)

                print('line_length: %s, step_size: %s, n_steps: %s'%(line_length, stepsize, int((line_length/(stepsize/1000)))))
                for i in range(int((line_length/(stepsize/1000))+0.5)):
                    new_dict = dict1.copy()
                    new_dict['X'] = float(dict1['X']) + (i+1)*x_step
                    new_dict['Y'] = float(dict1['Y']) + (i+1)*y_step
                    f.write(get_line(new_dict))
                    f.write('P1\n')
                    droplet_counter += 1
        else:
            f.write(lines[i])

    f.write(lines[-1])
    f.close()
    print('Number of droplets: %s'%(droplet_counter))
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
