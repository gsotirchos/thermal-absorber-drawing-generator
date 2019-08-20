from math import pi, degrees, sqrt, sin, cos, atan2, floor, ceil
from numpy import add as np_add, array
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
import instructions as instr


class Drawing:
    def __init__(self):
        self.DRAWING_HEIGHT = 4500
        self.DRAWING_WIDTH = int(self.DRAWING_HEIGHT/sqrt(2))
        self.OO = (int(self.DRAWING_WIDTH/2) + 100,
                   int(self.DRAWING_HEIGHT/2))
        self.MM = int(self.DRAWING_HEIGHT/4500)  # 1 mm ~ 1 px
        self.THIN = int(3*self.MM)
        self.THICK = int(5*self.MM)
        self.FONT_SIZE = 130*self.MM
        self.FONT = ImageFont.truetype("arial.ttf", self.FONT_SIZE)
        self.FONT_S = ImageFont.truetype("arial.ttf",
                                         int(self.FONT_SIZE/2))
        self.FONT_XS = ImageFont.truetype("arial.ttf",
                                          int(5*self.FONT_SIZE/11))

        self.drawing = Image.new('RGB', size=(self.DRAWING_WIDTH,
                                              self.DRAWING_HEIGHT),
                                 color='white')
        self.draw = ImageDraw.Draw(self.drawing)

        self.test_values = {'absorber_info': 'test_absorber',
                            'down_left_exit_closed': False,
                            'down_right_exit_closed': True,
                            'head_to_head': 950.0,
                            'header_diameter': 22.0,
                            'header_exit_length': 60.0,
                            'header_length': 2000.0,
                            'is_copper': False,
                            'is_horizontal': True,
                            'is_meander': False,
                            'is_painted': False,
                            'is_selective': True,
                            'is_selective04': False,
                            'is_strips': False,
                            'is_vertical': False,
                            'meander_width': 900.0,
                            'panel_holes': True,
                            'panel_length': 2000.0,
                            'panel_width': 1000.0,
                            'riser_count': 20,
                            'riser_diameter': 8.0,
                            'riser_edge_distance': 70.0,
                            'riser_step': 100.0,
                            'strip_overlap': 10.0,
                            'up_left_exit_closed': False,
                            'up_right_exit_closed': False}

        self.test_settings = {'P1': 6900.0,
                              'P2': 7000,
                              'P3': 6700,
                              'P4': 8200,
                              'Z1': 5,
                              'Z2': 4,
                              'acc': 350,
                              'f1': 155,
                              'f2': 125,
                              'f3': 160,
                              'f4': 109,
                              'pres': 1.6,
                              'pulse1': 0.3,
                              'pulse2': 0.4,
                              'pulse3': 0.3,
                              'pulse4': 0.4,
                              'vel': 210.0}

    def add(self, point1, point2):
        return tuple(np_add(point1, point2))

    def xy(self, point):
        return self.add(self.OO, (point[0], point[1]))

    def clear_drawing(self):
        self.drawing = Image.new('RGB', size=(self.DRAWING_WIDTH,
                                              self.DRAWING_HEIGHT),
                                 color='white')
        self.draw = ImageDraw.Draw(self.drawing)       

    def draw_dashed_line(self, start, end, dash, thickness=None,
                         color='black'):
        if thickness is None:
            thickness = self.THIN

        dl = sum(dash)
        ratios = [the_dash/dl for the_dash in dash]
        delta_x, delta_y = end[0] - start[0], end[1] - start[1]
        total_length = sqrt(delta_x**2 + delta_y**2)
        whole_parts = floor(total_length/dl)

        if whole_parts <= 0:
            return

        angle = atan2(delta_y, delta_x)
        dx, dy = dl*cos(angle), dl*sin(angle)

        # draw all whole parts
        part_end = start
        for i in range(whole_parts):
            for n in range(len(dash)):
                part_start = part_end
                part_end = self.add(part_start, (ratios[n]*dx,
                                                 ratios[n]*dy))

                if n % 2 == 0:
                    self.draw.line([part_start, part_end], color,
                                   thickness)

        # draw last part
        if total_length % dl != 0:
            part_start = self.add(start,
                                  (whole_parts*dx, whole_parts*dy))
            part_end = end

            self.draw.line([part_start, part_end], color, thickness)

    def draw_closed_exit(self, position, diameter, tube_angle,
                         thickness=None, color='black'):
        colors = (color, 'white')
        if thickness is None:
            thickness = self.THICK

        for i in range(2):
            t = (i - 0.5)*thickness
            self.draw.pieslice([self.add(position, (-diameter/2 + t,
                                                    -diameter/2 + t)),
                                self.add(position, (+diameter/2 - t,
                                                    +diameter/2 - t))],
                               degrees(pi-tube_angle),
                               degrees(-tube_angle),
                               colors[i], None)

    def draw_tube(self, start, end, diameter, closed_exit=(False, False),
                  thickness=None, color='black'):
        if thickness is None:
            thickness = self.THICK

        if start == end:
            return

        dx, dy = end[0] - start[0], end[1] - start[1]
        phi = atan2(dx, dy)
        x0l = start[0] - diameter/2*cos(phi)
        x0r = start[0] + diameter/2*cos(phi)
        y0l = start[1] + diameter/2*sin(phi)
        y0r = start[1] - diameter/2*sin(phi)
        x1l = x0l + dx
        x1r = x0r + dx
        y1l = y0l + dy
        y1r = y0r + dy

        # draw body
        self.draw.rectangle([(x0l, y0l), (x1r, y1r)], 'white', thickness)
        self.draw.line([(x0l, y0l), (x1l, y1l)], color, thickness)
        self.draw.line([(x0r, y0r), (x1r, y1r)], color, thickness)

        # draw exits
        if closed_exit[0]:
            self.draw_closed_exit(start, diameter, phi, thickness, color)

        if closed_exit[1]:
            self.draw_closed_exit(end, diameter, pi+phi, thickness,color)

        self.draw.line([(x0l, y0l), (x0r, y0r)], color, thickness)
        self.draw.line([(x1l, y1l), (x1r, y1r)], color, thickness)

    def draw_curve(self, center, variant, radius, diameter,
                   thickness=None, color='black'):
        colors = (color, 'white')
        if thickness is None:
            thickness = self.THICK

        theta2 = 90*variant
        theta1 = theta2 - 90

        for j in range(2):
            for i in range(2):
                r = radius + (0.5 - j)*diameter + (0.5 - i)*thickness
                start = self.add(center, (-r, -r))
                end = self.add(center, (+r, +r))

                self.draw.pieslice([start, end], theta1, theta2,
                                   colors[i], None)

    def draw_holes(self, panel_length, panel_width, lx, ly, radius):
        colors = ('black', 'white')

        # draw up-left and down-right holes
        for j in range(2):
            n = 2*j - 1
            for i in range(2):
                t = (0.5 - i)*self.THICK
                start = self.xy((n*(panel_width/2 - lx) - radius - t,
                                 n*(panel_length/2 - ly) - radius - t))
                end = self.xy((n*(panel_width/2 - lx) + radius + t,
                               n*(panel_length/2 - ly) + radius + t))

                self.draw.ellipse([start, end], colors[i], None)

    def draw_panel(self, panel_length, panel_width, has_holes=False):
        colors = ('black', 'white')

        for i in range(2):
            t = (0.5 - i)*self.THICK
            start = self.xy((-panel_width/2 - t, -panel_length/2 - t))
            end = self.xy((panel_width/2 + t, panel_length/2 + t))

            self.draw.rectangle([start, end], colors[i], None)

        if has_holes:
            lx = 50*self.MM
            ly = lx
            radius = 12*self.MM
            self.draw_holes(panel_length, panel_width, lx, ly, radius)

    def draw_strips(self, length, total_width, strip_step, strip_count):
        overlap = total_width - strip_count*strip_step
        self.draw_panel(length, total_width, has_holes=False)

        for i in range(1, strip_count):
            start1 = self.xy((-total_width/2 + i*strip_step, -length/2))
            end1 = self.add(start1, (0, length))
            start2 = self.add(start1, (overlap, 0))
            end2 = self.add(start2, (0, length))

            dash = (20*self.MM, 20*self.MM)
            self.draw.line([start1, end1], 'black', self.THICK)
            self.draw_dashed_line(start2, end2, dash)

    def draw_headers(self, diameter, head_to_head, header_length,
                     panel_width, exit_length, closed_exit,
                     is_horizontal):
        if isinstance(header_length, str):
            header_length = 0
        if is_horizontal:
            closed_exit = [closed_exit[i] for i in [0, 2, 1, 3]]

        for i in range(2):
            open_length = panel_width/2 + exit_length
            closed_length = header_length - open_length

            if closed_exit[2*i]:
                length_start = -closed_length
                length_end = open_length
            elif closed_exit[1+2*i]:
                length_start = -open_length
                length_end = closed_length
            else:
                length_start = -open_length
                length_end = open_length

            if is_horizontal:
                start = self.xy(((2*i-1)*head_to_head/2, length_start))
                end = self.xy(((2*i-1)*head_to_head/2, length_end))
            else:
                start = self.xy((length_start, (2*i-1)*head_to_head/2))
                end = self.xy((length_end, (2*i-1)*head_to_head/2))

            self.draw_tube(start, end, diameter, closed_exit[2*i:2*i+2])

    def draw_riser_grid(self, start_x, length, riser_count, step,
                        diameter, direction='v'):
        for i in range(riser_count):
            x = start_x - i*step
            y = length/2

            if direction.lower() == 'v':
                riser_start = self.xy((x, -y))
                riser_end = self.xy((x, y))
            elif direction.lower() == 'h':
                riser_start = self.xy((-y, x))
                riser_end = self.xy((y, x))

            self.draw_tube(riser_start, riser_end, diameter)

    def draw_riser_meander(self, edge_distance, meander_width,
                           length, riser_count, width, step, diameter):
        mm = self.MM
        def add(point1, point2): return self.add(point1, point2)
        def xy(point): return self.xy(point)
        link_thickness = 12
        radius = 30
        if step < 2*radius:
            radius = step/2
        offset = 77

        for i in range(riser_count):
            riser_start = xy(((-width/2 + radius + edge_distance)*mm,
                              (length/2 - offset - i*step)*mm))
            riser_end = add(riser_start, ((meander_width - 2*radius)*mm,
                                          0))

            # draw first link
            if i == 0:
                link_start = add(riser_end, (-link_thickness/2*mm,
                                             offset*mm))
                link_end = add(link_start, (0, -offset*mm))
                self.draw_tube(link_start, link_end, link_thickness*mm)

            # draw curved segments
            n = i % 2
            nradius = (1 - 2*n)*radius
            self.draw_curve(add(riser_start, (0, nradius*mm)), 3-n,
                            radius*mm, diameter*mm)
            self.draw_curve(add(riser_end, (0, -nradius*mm)), 1+3*n,
                            radius*mm, diameter*mm)

            # draw horizontal riser segments
            self.draw_tube(riser_start, riser_end, diameter*mm)

            # draw verical riser segments
            ver_start = add(riser_end, ((radius - n*meander_width)*mm,
                                        -radius*mm))
            if i != riser_count - 1:
                ver_end = add(ver_start, (0, (-step + 2*radius)*mm))
            else:
                ver_end = xy((0, -length/2*mm))
                ver_end = (ver_start[0], ver_end[1])

            self.draw_tube(ver_start, ver_end, diameter*mm)

        # draw last link
        distance = (2*n-1)*(meander_width - radius - link_thickness/2)
        link2_start = add(ver_start, (distance*mm,
                                      (radius-diameter/2)*mm))
        link2_end = add(ver_end, (distance*mm, 0))

        self.draw_tube(link2_start, link2_end, link_thickness*mm)

        # draw inlet
        inlet_start = xy(((-width/2 + edge_distance)*mm, length/2*mm))
        inlet_end = add(inlet_start, (0, (-offset + radius)*mm))

        self.draw_tube(inlet_start, inlet_end, diameter*mm)

    def draw_risers(self, diameter, edge_distance, riser_length,
                    riser_count, total_width, step, is_horizontal,
                    is_meander, meander_width):
        if is_meander:
            self.draw_riser_meander(edge_distance, meander_width,
                                    riser_length, riser_count,
                                    total_width, step, diameter)
            return
        elif is_horizontal:
            direction = 'h'
        else:
            direction = 'v'

        start = total_width/2 - edge_distance
        self.draw_riser_grid(start, riser_length, riser_count, step,
                             diameter, direction)

    def draw_arrow(self, start, mid, end, color='black', thickness=None,
                   arrow_count=2):
        if thickness is None:
            thickness = self.THICK
        arrowhead_width = 7*thickness
        arrowhead_length = 1.5*arrowhead_width
        dx, dy = mid[0] - start[0], mid[1] - start[1]
        theta = atan2(dy, dx)
        rot = array([[cos(theta), -sin(theta)],
                     [sin(theta), cos(theta)]])
        if sqrt(dx**2 + dy**2) < 2.5*arrowhead_length:
            is_in = -1
        else:
            is_in = 1

        # set each arrowhead's 3-points
        point = [[], []]
        point[0] = [start, [], []]
        point[1] = [mid, [], []]
        for the_arrow in range(2):
            n = 1 - 2*the_arrow
            for the_point in range(1, 3):
                m = 3 - 2*the_point
                du = array([n*is_in*arrowhead_length,
                            m*arrowhead_width/2])
                rot_du = tuple(rot.dot(du))
                point[the_arrow][the_point] = \
                    self.add(point[the_arrow][0], rot_du)

            # print('arrow ' + str(the_arrow) + ':')
            # pprint(point[the_arrow])

            # draw arrowhead
            if the_arrow < arrow_count:
                self.draw.polygon(point[the_arrow], color, None)

        end2 = end
        start1 = ((point[0][1][0] + point[0][2][0])/2,
                  (point[0][1][1] + point[0][2][1])/2)
        start2 = ((point[1][1][0] + point[1][2][0])/2,
                  (point[1][1][1] + point[1][2][1])/2)
        if arrow_count == 1:
            start2 = mid
        if is_in == -1:
            du = array([-arrowhead_length, 0])
            rot_du = tuple(rot.dot(du))
            end1 = self.add(start1, rot_du)
        elif is_in == 1:
            end1 = start2

        # draw arrow line and dimension line
        self.draw.line([start1, end1], color, thickness)
        self.draw.line([start2, end2], color, thickness)

    def draw_dimension(self, point1, point2, label, steps='',
                       extra_offset=0, color='blue', arrows=2):
        def add(point1, point2): return self.add(point1, point2)
        FONT = self.FONT
        FONT_S = self.FONT_S
        FONT_SIZE = self.FONT_SIZE
        ARR_LENGTH = 10*self.THICK

        # if the length is 0 don't draw dimension
        if point1 == point2:
            return

        offset = 2*ARR_LENGTH + extra_offset

        # determine textbox dimensions
        label_size = self.draw.textsize(label, FONT)
        steps_size = self.draw.textsize(steps, FONT_S)
        text_size = (label_size[0] + steps_size[0],
                     max(label_size[1], steps_size[1]))

        # define dimension line parameters
        start, mid = point1, point2
        dx, dy = mid[0] - start[0], mid[1] - start[1]
        theta = atan2(dy, dx)
        dl = (cos(theta)*text_size[0], sin(theta)*text_size[1])
        offset_dl = add(dl, (cos(theta)*offset, sin(theta)*offset))

        # determine if label fits inside dimension and set end point
        if sqrt(dl[0]**2+dl[1]**2) + 2*ARR_LENGTH < sqrt(dx**2+dy**2):
            # is in
            end = ((start[0] + mid[0])/2, ((start[1] + mid[1])/2))
            text_xy = add(end, (-abs(dl[0]/2), abs(dl[1]/2) - FONT_SIZE))
        else:
            # is out
            end = add(mid, offset_dl)
            if theta == 0:
                text_xy = add(end, (-text_size[0], -FONT_SIZE))
            elif 0 < theta < pi/2:
                text_xy = add(end, (0, -FONT_SIZE))
            elif theta == pi/2:
                text_xy = add(end, (0, -FONT_SIZE))
            elif pi/2 < theta < pi:
                text_xy = add(end, (-text_size[0], -FONT_SIZE))
            elif theta == pi or theta == -pi:
                text_xy = add(end, (0, -FONT_SIZE))
            elif -pi < theta < -pi/2:
                text_xy = add(end, (-text_size[0], -FONT_SIZE))
            elif theta == -pi/2:
                text_xy = add(end, (0, 0))
            elif -pi/2 < theta < 0:
                text_xy = add(end, (0, -FONT_SIZE))

        self.draw_arrow(start, mid, end, color, arrow_count=arrows)

        self.draw.text(text_xy, label, color, FONT)
        self.draw.text(add(text_xy, (label_size[0] + 15*self.MM, 0)),
                       steps, 'black', FONT_S)

    def write_instruction(self, operator, location, n, m, color='black',
                          font=None):
        if font is None:
            if operator == 1:
                font = self.FONT_S
            elif operator == 2:
                font = self.FONT_S

        text = ' ' + instr.step[n][m]
        if m != 0:
            text = str(m) + '.' + text
        if n != 0:
            text = str(n) + '.' + text

        if operator == 1:
            self.draw.text(location, text, color, font)
        elif operator == 2:
            self.draw.text(location, text, color, font)

    def make_labels_and_steps(self, values):
        labels = {}
        for key, value in values.items():
            if key == 'absorber_info':
                labels[key] = value
            else:
                labels[key] = str(value).rstrip('0').rstrip('.')

        steps = {
            'riser_step': '1.6, 6.2,\n2.4.2.3',
            'header_exit_length': '4.3.2.2\n7.1',
            'riser_edge_distance': '4.3.2.2\n7.2',
            'table_edge_distance': '2.1.2',
            'strip_step': '',
            'panel_residual': '4.3.1.1.4',
            'diagonals': '7.3'
        }

        return labels, steps

    def make_base_drawing(self, values):
        mm = self.MM

        # define parameters
        closed_exit = (values['up_left_exit_closed'],
                       values['up_right_exit_closed'],
                       values['down_left_exit_closed'],
                       values['down_right_exit_closed'])

        if values['is_horizontal']:
            total_width = values['panel_length']
        else:
            total_width = values['panel_width']

        # draw panel/strips
        if values['is_strips']:
            self.draw_strips(values['panel_length']*mm,
                             values['panel_width']*mm,
                             values['riser_step']*mm,
                             values['riser_count'])
        else:
            self.draw_panel(values['panel_length']*mm,
                            values['panel_width']*mm,
                            has_holes=values['panel_holes'])

        # draw risers
        self.draw_risers(values['riser_diameter']*mm,
                         values['riser_edge_distance']*mm,
                         (values['head_to_head'] -
                          values['header_diameter'])*mm,
                         values['riser_count'],
                         total_width*mm,
                         values['riser_step']*mm,
                         values['is_horizontal'],
                         values['is_meander'],
                         values['meander_width'])

        # draw headers
        self.draw_headers(values['header_diameter']*mm,
                          values['head_to_head']*mm,
                          values['header_length']*mm,
                          total_width*mm,
                          values['header_exit_length']*mm,
                          closed_exit, values['is_horizontal'])

    def make_dimensions(self, values):
        mm = self.MM
        def xy(point): return self.xy(point)
        def add(point1, point2): return self.add(point1, point2)
        CHANNEL_LEN = 250
        CHANNEL_WID = 7
        TABLE_WIDTH = 1533
        DISTANCE = 175

        # set necessary parameters
        if values['is_horizontal']:
            total_width = values['panel_length']
            total_length = values['panel_width']
        else:
            total_width = values['panel_width']
            total_length = values['panel_length']

        closed_exit = [values['up_right_exit_closed'],
                       values['down_right_exit_closed'],
                       values['down_left_exit_closed'],
                       values['up_left_exit_closed']]

        if values['is_horizontal']:
            closed_exit = [closed_exit[i] for i in [2, 1, 0, 3]]

        labels, steps = self.make_labels_and_steps(values)

        # draw upper/lower panel residual's length
        panel_residual = (total_length - values['head_to_head'] -
                          values['header_diameter'])/2
        residual_label = str(abs(panel_residual)).rstrip('0').rstrip('.')

        if closed_exit[1:3] == [False, False]:
            n = 1
        else:
            n = -1
        point2 = (0, n*total_length/2*mm)
        point1 = add(point2, (0, -n*panel_residual*mm))

        if panel_residual < 0:
            point1, point2 = point2, point1

        if values['is_horizontal']:
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw_dimension(xy(point1), xy(point2), residual_label,
                            steps['panel_residual'],
                            extra_offset=-75*mm)

        # draw diagonal's quality check
        if not (closed_exit[0:2] == [True, True] or
                closed_exit[2:4] == [True, True]):
            point1 = (-(total_width/2 + values['header_exit_length'])*mm,
                      (values['head_to_head'] -
                       values['header_diameter'])/2*mm)
            point2 = (-point1[0], -point1[1])

            if values['is_horizontal']:
                point1 = (point1[1], point1[0])
                point2 = (point2[1], point2[0])

            if closed_exit[0] or closed_exit[2]:
                point1 = (-point1[0], point1[1])
                point2 = (-point2[0], point2[1])
        else:
            if values['is_vertical'] or values['is_strips']:
                point2 = ((total_width/2 + values['riser_diameter']/2 -
                          values['riser_edge_distance'])*mm,
                          -(values['head_to_head'] -
                            values['header_diameter'])/2*mm)
                point1 = (point2[0] -
                          ((values['riser_count']-1)*values['riser_step']
                           + values['riser_diameter'])*mm,
                          -point2[1])

        label = (str(round(sqrt((2*point1[0])**2+(2*point1[1])**2),
                           1)).rstrip('0').rstrip('.'))
        self.draw_dimension(xy(point1), xy(point2), label,
                            steps['diagonals'])

        # draw header exit length
        if closed_exit[1]:
            n = -1
        else:
            n = 1

        l_start = (n*(total_width/2 + values['header_exit_length'])*mm,
                   (values['head_to_head']/2)*mm -
                   values['header_diameter']/2 - self.THICK)
        l_end = add(l_start, (0, -70*mm))
        point2 = add(l_start, (0, -50*mm))
        point1 = add(point2, (-n*values['header_exit_length']*mm, 0))

        if values['is_horizontal']:
            l_start = (l_start[1], l_start[0])
            l_end = (l_end[1], l_end[0])
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw.line([xy(l_start), xy(l_end)], 'blue', self.THIN)
        self.draw_dimension(xy(point1), xy(point2),
                            labels['header_exit_length'],
                            steps['header_exit_length'])

        # draw riser-edge distance
        point2 = (total_width/2*mm, -total_length/3*mm)
        point1 = add(point2, (-values['riser_edge_distance']*mm, 0))

        if values['is_meander']:
            point1 = (-point1[0], -point1[1])
            point2 = (-point2[0], -point2[1])
            l_start = add(point1, (0, -values['riser_step']/2*mm))
            l_end = add(point1, (0, values['riser_step']/2*mm))
            self.draw.line([xy(l_start), xy(l_end)], 'blue',
                           self.THIN)
        elif values['is_horizontal']:
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw_dimension(xy(point1), xy(point2),
                            labels['riser_edge_distance'],
                            steps['riser_edge_distance'],
                            extra_offset=60*mm)

        # draw riser step
        if values['is_meander']:
            point2 = ((-values['head_to_head'] +
                       (values['head_to_head'] - 77) %
                       values['riser_step'])*mm, 0)
            point1 = add(point2, (values['riser_step']*mm, 0))
        else:
            point2 = ((total_width/2 - values['riser_edge_distance'])*mm,
                      -total_length/6*mm)
            point1 = add(point2, (-values['riser_step']*mm, 0))

            if values['is_horizontal']:
                point1 = (point1[1], point1[0])
                point2 = (point2[1], point2[0])

        self.draw_dimension(xy(point1), xy(point2), labels['riser_step'],
                            steps['riser_step'])

        # draw distance from table's right edge
        if values['is_vertical'] or values['is_strips']:
            for j in range(2):  # Y-axis symmetry
                if TABLE_WIDTH - values['panel_width'] < DISTANCE:
                    distance = (TABLE_WIDTH-values['panel_width'])/2
                else:
                    distance = DISTANCE

                label = str(abs(distance)).rstrip('0').rstrip('.')
                step = steps['table_edge_distance']

                channel_mid = ((1-2*j)*(total_width/2 + distance)*mm,
                               total_length/4*mm)
                channel_start = add(channel_mid,
                                    (0, -CHANNEL_LEN/2*mm))
                channel_end = add(channel_mid, (0, CHANNEL_LEN/2*mm))
                point1 = (channel_mid[0] - (1-2*j)*distance*mm,
                          channel_mid[1])
                point2 = add(point1, ((1-2*j)*distance*mm, 0))

                if distance < 0:
                    point1, point2 = point2, point1
                elif distance >= DISTANCE and j == 1:
                    point2 = point1
                    channel_end = channel_start

                self.draw_tube(xy(channel_start), xy(channel_end),
                               CHANNEL_WID*mm, thickness=self.THIN,
                               color='blue')
                self.draw_dimension(xy(point1), xy(point2), label,
                                    step)

        # draw strip width
        if values['is_strips']:
            strip_width = (total_width - (values['riser_count']-1) *
                           values['riser_step'])
            point2 = (-total_width/2*mm, -total_length/4*mm)
            point1 = add(point2, (strip_width*mm, 0))
            label = (str(strip_width).rstrip('0').rstrip('.'))
            self.draw_dimension(xy(point1), xy(point2), label,
                                steps['strip_step'], color='black')

        # set offsets
        if values['is_horizontal']:
            offset_h = 60
            offset_v = 750
        else:
            offset_h = 300
            offset_v = 360

        # draw closed header length:
        if closed_exit[1:3] == [False, False]:
            n = 1
        else:
            n = -1

        if isinstance(values['header_length'], str):
            values['header_length'] = 0
        open_length = total_width/2 + values['header_exit_length']
        closed_length = values['header_length'] - open_length

        if closed_exit[int((n+5)/2)]:
            length_left = -closed_length - values['header_diameter']/2
            length_right = open_length
            label = str(values['header_length']).rstrip('0').rstrip('.')
        elif closed_exit[int((1-n)/2)]:
            length_left = -open_length
            length_right = closed_length + values['header_diameter']/2
            label = str(values['header_length']).rstrip('0').rstrip('.')
        else:
            length_left = -open_length
            length_right = open_length
            label = (str(round(total_width +
                     2*values['header_exit_length'], 1))
                     .rstrip('0').rstrip('.'))

        l_1_start = (length_left*mm, n*((-values['head_to_head'] -
                     values['header_diameter'])/2*mm - self.THICK))
        l_1_end = add(l_1_start, (0, -n*offset_v*mm))
        l_2_start = (length_right, l_1_start[1])
        l_2_end = (length_right, l_1_end[1])
        point1 = add(l_1_end, (0, n*50*mm))
        point2 = add(l_2_end, (0, n*50*mm))

        if values['is_horizontal']:
            l_1_start = (l_1_start[1], l_1_start[0])
            l_1_end = (l_1_end[1], l_1_end[0])
            l_2_start = (l_2_start[1], l_2_start[0])
            l_2_end = (l_2_end[1], l_2_end[0])
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw.line([xy(l_1_start), xy(l_1_end)], 'black', self.THIN)
        self.draw.line([xy(l_2_start), xy(l_2_end)], 'black', self.THIN)
        self.draw_dimension(xy(point1), xy(point2), label, color='black')

        # draw head-to-head distance
        dash_1_start = ((-total_width/2 + 150)*mm,
                        -values['head_to_head']/2*mm)
        dash_1_end = ((-total_width/2 - values['header_exit_length'] -
                       50)*mm, dash_1_start[1])
        l_1_start = dash_1_end
        l_1_end = add(l_1_start, (-offset_h*mm, 0))
        dash_2_start = (dash_1_start[0], -dash_1_start[1])
        dash_2_end = (dash_1_end[0], -dash_1_end[1])
        l_2_start = (l_1_start[0], -l_1_start[1])
        l_2_end = (l_1_end[0], -l_1_end[1])
        point1 = add(l_1_end, (50*mm, 0))
        point2 = add(l_2_end, (50*mm, 0))

        if values['is_horizontal']:
            dash_1_start = (dash_1_start[1], dash_1_start[0])
            dash_1_end = (dash_1_end[1], dash_1_end[0])
            dash_2_start = (dash_2_start[1], dash_2_start[0])
            dash_2_end = (dash_2_end[1], dash_2_end[0])
            l_1_start = (l_1_start[1], l_1_start[0])
            l_1_end = (l_1_end[1], l_1_end[0])
            l_2_start = (l_2_start[1], l_2_start[0])
            l_2_end = (l_2_end[1], l_2_end[0])
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        label = str(values['head_to_head']).rstrip('0').rstrip('.')
        dash = (80*mm, 10*mm, 10*mm, 10*mm)
        self.draw_dashed_line(xy(dash_1_start), xy(dash_1_end), dash,
                              self.THIN)
        self.draw_dashed_line(xy(dash_2_start), xy(dash_2_end), dash,
                              self.THIN)
        self.draw.line([xy(l_1_start), xy(l_1_end)], 'black', self.THIN)
        self.draw.line([xy(l_2_start), xy(l_2_end)], 'black', self.THIN)
        self.draw_dimension(xy(point1), xy(point2), label, color='black')

        # set offsets
        if values['is_horizontal']:
            offset_h = 360
            offset_v = 400
        else:
            offset_h = 750
            offset_v = 200

        # draw panel width
        if closed_exit[1:3] == [False, False]:
            n = 1
        else:
            n = -1

        label = str(total_width).rstrip('0').rstrip('.')
        l_1_start = (-total_width/2*mm,
                     -n*(total_length/2*mm-2*self.THIN))
        l_1_end = add(l_1_start, (0, -n*offset_v*mm))
        l_2_start = (-l_1_start[0], l_1_start[1])
        l_2_end = (-l_1_end[0], l_1_end[1])
        point1 = add(l_1_end, (0, n*50*mm))
        point2 = add(l_2_end, (0, n*50*mm))

        if values['is_horizontal']:
            l_1_start = (l_1_start[1], l_1_start[0])
            l_1_end = (l_1_end[1], l_1_end[0])
            l_2_start = (l_2_start[1], l_2_start[0])
            l_2_end = (l_2_end[1], l_2_end[0])
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw.line([xy(l_1_start), xy(l_1_end)], 'black', self.THIN)
        self.draw.line([xy(l_2_start), xy(l_2_end)], 'black', self.THIN)
        self.draw_dimension(xy(point1), xy(point2), label, color='black')

        # draw panel length
        label = str(total_length).rstrip('0').rstrip('.')
        l_1_start = (-total_width/2*mm-2*self.THIN, -total_length/2*mm)
        l_1_end = add(l_1_start, (-offset_h*mm, 0))
        l_2_start = (l_1_start[0], -l_1_start[1])
        l_2_end = (l_1_end[0], -l_1_end[1])
        point1 = add(l_1_end, (50*mm, 0))
        point2 = add(l_2_end, (50*mm, 0))

        if values['is_horizontal']:
            l_1_start = (l_1_start[1], l_1_start[0])
            l_1_end = (l_1_end[1], l_1_end[0])
            l_2_start = (l_2_start[1], l_2_start[0])
            l_2_end = (l_2_end[1], l_2_end[0])
            point1 = (point1[1], point1[0])
            point2 = (point2[1], point2[0])

        self.draw.line([xy(l_1_start), xy(l_1_end)], 'black', self.THIN)
        self.draw.line([xy(l_2_start), xy(l_2_end)], 'black', self.THIN)
        self.draw_dimension(xy(point1), xy(point2), label, color='black')

    def make_order_info(self, values, settings):
        FONT, FONT_S = self.FONT, self.FONT_S
        FONT_SIZE = self.FONT_SIZE
        SPCING = int(self.FONT_SIZE/5)

        # draw absorber info
        label = values['absorber_info']
        text_size = self.draw.textsize(label, FONT)
        text_xy = ((self.DRAWING_WIDTH - text_size[0])/2, FONT_SIZE)
        self.draw.text(text_xy, label, 'black', FONT, spacing=SPCING)

        # draw coordinate system
        x_label = ' I'
        y_label = 'II'
        if values['is_horizontal']:
            x_label, y_label = y_label, x_label

        origin_xy = (3*self.FONT_SIZE,
                     self.DRAWING_HEIGHT - 4*self.FONT_SIZE)
        self.draw_dimension(self.add(origin_xy, (400, 0)), origin_xy,
                            x_label, color='black', arrows=1)
        self.draw_dimension(self.add(origin_xy, (0, -400)), origin_xy,
                            y_label, color='black', arrows=1)

        # print material info
        label = ''
        # if values['is_selective']:
        #     panel_material_text = 'επιλεκτικό'
        # elif values['is_selective04']:
        #     panel_material_text = 'επιλεκτικό 0.4'
        # elif values['is_painted']:
        #     panel_material_text = 'βαμμένο'
        # elif values['is_copper']:
        #     panel_material_text = 'από χαλκό'
        # if values['is_strips']:
        #     panel_type_text = str(values['riser_count']) + ' Φινάκια'
        # else:
        #     panel_type_text = 'Φύλλο'
        # label = (panel_type_text + ': ' + panel_material_text + ', ' +
        #          str(round(values['panel_length'])) + 'X' +
        #          str(round(values['panel_width'])))
        label += ('\nΣωλήνες: Ø' + str(round(values['header_diameter']))
                  + ', Ø' + str(round(values['riser_diameter'])))
        text_size = self.draw.textsize(label, FONT_S)
        text_xy = (FONT_SIZE,
                   self.DRAWING_HEIGHT - text_size[1] - FONT_SIZE)
        self.draw.text(text_xy, label, 'black', FONT_S, spacing=SPCING)

        # print laser & machine settings info
        setting = {}
        if values['riser_diameter'] <= 8:
            setting['Z'] = settings['Z1']
        else:
            setting['Z'] = settings['Z2']
        if values['is_selective']:
            for item in ('P', 'pulse', 'f'):
                setting[item] = settings[item + '1']
        if values['is_selective04']:
            for item in ('P', 'pulse', 'f'):
                setting[item] = settings[item + '2']
        if values['is_tss']:
            for item in ('P', 'pulse', 'f'):
                setting[item] = settings[item + '3']
        if values['is_painted']:
            for item in ('P', 'pulse', 'f'):
                setting[item] = settings[item + '4']
        if values['is_copper']:
            for item in ('P', 'pulse', 'f'):
                setting[item] = settings[item + '5']

        label_l = ('VEL: ' + str(settings['vel']) + '\n' +
                   'ACC: ' + str(settings['acc']) + '\n' +
                   'PRES: ' + str(settings['pres']) + '\n' +
                   'Z: ' + str(setting['Z']) + '\n')
        label_r = ('POWER: ' + str(setting['P']) + '\n' +
                   'PULSE: ' + str(setting['pulse']) + '\n' +
                   'FREQ: ' + str(setting['f']))
        text_l_size = self.add(self.draw.textsize(label_l, FONT_S),
                               (int(FONT_SIZE/2), 0))
        text_r_size = self.draw.textsize(label_r, FONT_S)
        text_size = (text_l_size[0] + text_r_size[0],
                     max(text_l_size[1], text_r_size[1]))
        text_xy = (self.DRAWING_WIDTH - FONT_SIZE - text_size[0],
                   self.DRAWING_HEIGHT - FONT_SIZE - text_size[1])
        self.draw.text(text_xy, label_l, 'black', FONT_S, spacing=SPCING)
        self.draw.text(self.add(text_xy, (text_l_size[0], 0)), label_r,
                       'black', FONT_S, spacing=SPCING)

    def make_order_instructions_page_1(self, values):
        # write instructions for operator 1
        location = [2*self.FONT_SIZE, 2*self.FONT_SIZE]

        self.draw.text(location, 'Χρήσιμα βήματα:', 'black', self.FONT)
        location[1] += int(2.5*self.FONT_SIZE)

        for n in range(1, 8):
            if n == 5 and values['riser_diameter'] == 8:
                continue
            self.write_instruction(1, location, n, 0)
            location[1] += 2*self.FONT_SIZE

    def make_order_instructions_page_2(self, values):
        # write instructions for operator 2
        location = [self.FONT_SIZE, self.FONT_SIZE]

        self.draw.text(location, 'Χρήσιμα υπο-βήματα:', 'black',
                       self.FONT)
        location[1] += int(2.5*self.FONT_SIZE)

        for n in range(1, 8):
            if n == 5 and values['riser_diameter'] == 8:
                continue

            for m in range(len(instr.step[n])):
                # n = 1
                if n == 1:
                    if not values['panel_holes']:
                        if m == 3:
                            continue
                    if not values['is_meander']:
                        if m == 5:
                            continue
                    if not values['is_strips']:
                        if m in (6, 7):
                            continue

                # n = 2
                if n == 2 and not values['is_strips']:
                    if m in (3, 4, 5):
                        continue
                elif n == 2 and values['is_strips']:
                    if m in (1, 2):
                        continue

                # n = 3
                if n == 3 and (values['is_vertical'] or
                               values['is_strips']):
                    if m in (3, 4, 5):
                        continue
                elif n == 3 and not (values['is_vertical'] or
                                     values['is_strips']):
                    if m == 2:
                        continue

                # skip super-steps
                if m != 0:
                    self.write_instruction(2, location, n, m)
                if not (n == 1 and m == 0):
                    location[1] += self.FONT_SIZE/1.4

                if m == 0:
                    if n in (1, 7):
                        hard_order_text = '(Χωρίς αυστηρή διαδοχή)'
                    else:
                        hard_order_text = '(Με αυστηρή διαδοχή)'

                    location[1] -= 0.5*self.FONT_SIZE/1.3
                    self.draw.text(location, hard_order_text, 'black',
                                   self.FONT_XS)
                    location[1] += self.FONT_SIZE/1.3

    def make_job_order(self, file_name, values, settings):
        self.make_base_drawing(values)
        self.make_dimensions(values)
        self.make_order_info(values, settings)
        self.drawing.save(file_name, 'PDF')

        self.clear_drawing()
        self.make_order_instructions_page_1(values)
        self.drawing.save(file_name, 'PDF', append=True)

        self.clear_drawing()
        self.make_order_instructions_page_2(values)
        self.drawing.save(file_name, 'PDF', append=True)


# TEST
# drawing = Drawing()
# 
# drawing.make_job_order('C:\\Users\\George\\Desktop\\test.pdf',
#                        drawing.test_values,
#                        drawing.test_settings)
