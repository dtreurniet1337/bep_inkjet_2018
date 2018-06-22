from tkinter import *
from tkinter import filedialog
import tkinter
import time
import subprocess



STAGE_RANGE = (26, 26) #mm


class GcodeModule(Frame):
    def __init__(self, root, master):
        self.root = root
        self.master = master
        self.frame = Frame(self.root, relief=GROOVE,border=1)

        self.open_bt = Button(self.frame, text='Open file', command=self.open_pressed)
        self.selected_file = ''

        self.canvas = Canvas(self.frame, bg='white', width=500, height=500)

        self.interpolate_bt = Button(self.frame, text="Interpolate...", command=self.interp_pressed, state=DISABLED)
        self.print_bt = Button(self.frame, text='Print', command=self.print_pressed, state=DISABLED)

        self.open_bt.grid(row=1, column=1, columnspan=2, sticky='W')
        self.canvas.grid(row=2, column=1, columnspan=2)
        self.interpolate_bt.grid(row=3, column=1)
        self.print_bt.grid(row=3, column=2)


    def print_pressed(self):
        self.master.status_module.set_status_light('yellow')
        self.master.connect_module.print_file(self.selected_file)
        self.master.status_module.set_status_light('green')
        return True

    def interp_pressed(self):
        dialog = GcodeProcessorDialog(self, self.selected_file)

    def open_pressed(self, select_new=True):
        if select_new:
            self.selected_file = filedialog.askopenfilename(initialdir="./gcode/")
        self.canvas.delete('all')
        if self.selected_file[-3:] != '.nc':
            self.selected_file = ''
            self.interpolate_bt['state'] = DISABLED
            self.print_bt['state'] = DISABLED
        else:
            self.draw_gcode()
            self.interpolate_bt['state'] = NORMAL
            self.print_bt['state'] = NORMAL


    def draw_gcode(self):
        if not self.selected_file: return
        self.canvas.delete('all')

        def get_gcode_dict(gcode):
            gcode_list = gcode.split(' ')
            gcode_dict = {}
            for i in gcode_list:
                gcode_dict[i[0]] = i[1:]
            return gcode_dict

        def draw_line(coords, fill=None):
            coords = [i*scale for i in coords]
            coords[1] = float(self.canvas['height'])-coords[1]
            coords[3] = float(self.canvas['height'])-coords[3]
            line = self.canvas.create_line(coords[0], coords[1], coords[2], coords[3], fill=fill)

        def draw_dot(coord, radius, fill=None):
            x0 = (scale * coord[0]) - radius
            y0 = float(self.canvas['height'])-(scale*coord[1]) - radius
            x1 = (scale * coord[0]) + radius
            y1 = float(self.canvas['height'])-(scale*coord[1]) + radius

            dot = self.canvas.create_oval(x0, y0, x1, y1, fill=fill)

        # Read Gcode
        try:
            gcode = open(self.selected_file)
        except Exception as e:
            print('Failed to draw Gcode: %s'%(e))
        gcode_lines = gcode.readlines()
        gcode.close()

        # Determine Gcode max coords
        max_coords = [0,0]
        for line in gcode_lines:
            code = get_gcode_dict(line)
            if 'G' in code:
                if code['G'] == '1':
                    if float(code['X']) > max_coords[0]: max_coords[0] = float(code['X'])
                    if float(code['Y']) > max_coords[1]: max_coords[1] = float(code['Y'])


        # Draw Gcode
        current_coords = [0, 0]
        scale = float(self.canvas['height'])/(1.1*max(max_coords))
        for line in gcode_lines:
            code = get_gcode_dict(line)
            if 'G' in code:
                if code['G'] == '0':
                    coords = (current_coords[0], current_coords[1], float(code['X']), float(code['Y']))
                    current_coords = [float(code['X']), float(code['Y'])]
                    draw_line(coords, fill='blue')
                    draw_dot((float(code['X']), float(code['Y'])), 1, fill='black')
                if code['G'] == '1':
                    coords = (current_coords[0], current_coords[1], float(code['X']), float(code['Y']))
                    current_coords = [float(code['X']), float(code['Y'])]
                    draw_line(coords, fill='red')
                    draw_dot((float(code['X']), float(code['Y'])), 1, fill='black')

        # Write filename
        self.canvas.create_text(10, 30, fill='darkblue', text=self.selected_file, anchor=NW)


        # Write dimensions
        text_dim = str(max_coords[0]) + 'x' + str(max_coords[1]) + 'mm'
        self.canvas.create_text(10, 10, fill='darkblue', text=text_dim, anchor=NW)



from script import interpolate_gcode as interp
class GcodeProcessorDialog():
    def __init__(self, master, gcode_file):
        self.root = Tk()
        self.master = master
        self.frame = Frame(self.root, padx=5, pady=5)
        self.gcode_file = gcode_file

        self.lbl_spacing = Label(self.frame, text='Droplet spacing')
        self.ent_spacing = Entry(self.frame)
        self.lbl_spacing_unit = Label(self.frame, text='um')


        self.bt_interp = Button(self.frame, text='Interpolate!', command=self.interp_pressed)


        self.frame.grid(row=1, column=1)

        self.lbl_spacing.grid(row=1, column=1, sticky='W')
        self.ent_spacing.grid(row=1, column=2, sticky='W')
        self.lbl_spacing_unit.grid(row=1, column=3, sticky='W')

        self.bt_interp.grid(row=2, column=1)

        self.root.title('Interpolate Gcode')
        self.root.mainloop()




    def interp_pressed(self):
        try:
            entry = float(self.ent_spacing.get().strip())
        except Exception as e:
            print('Invalid entry')
            return
        new_file = interp.interpolate_gcode(self.gcode_file, entry)
        self.master.selected_file = new_file
        self.master.open_pressed(select_new=False)
        self.root.destroy()
