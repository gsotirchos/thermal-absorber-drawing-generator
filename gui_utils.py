import sys
from os import environ, path
from drawing_utils import Drawing
from file_utils import FileManager
import re
# from pprint import pprint

if sys.version_info[0] >= 3:
    import PySimpleGUI as sg
else:
    import PySimpleGUI27 as sg


class Gui:
    def __init__(self):
        LCOL_WIDTH = 21
        FRAME_LCOL_WIDTH = 6
        FRAME2_LCOL_WIDTH = 13
        SETTINGS_LCOL_WIDTH = 8
        SETTINGS2_LCOL_WIDTH = 3
        TB_WID = 7
        self.was_horizontal = False

        HOMEPATH = 'C:' + environ['HOMEPATH']
        if getattr(sys, 'frozen', False):
            CURRENT_DIR = path.dirname(path.realpath(sys.executable))
        elif __file__:
            CURRENT_DIR = path.dirname(path.realpath(__file__))
        self.guessed_name = 'job_order'
        self.default_output_folder = HOMEPATH + '\\Desktop\\'
        self.output_file = (self.default_output_folder +
                            self.guessed_name + '.pdf')
        self.OLDS_DIR = 'old'
        self.SETTINGS_FILE = CURRENT_DIR + '\\settings.txt'
        self.SETTINGS_FILE_EXISTS = path.isfile(self.SETTINGS_FILE)

        # machine default settings
        self.default_settings = {
            'vel': 210,
            'acc': 350,
            'pres': 1.6,
            'Z1': 5,  # Z for riser diam. 8 or smaller
            'Z2': 4,  # Z for riser larger than diam. 8
            'P1': 6900,     # -------------------
            'pulse1': 0.3,  # -  for selective  -
            'f1': 155,      # -------------------
            'P2': 7000,     # -------------------
            'pulse2': 0.4,  # - for selective04 -
            'f2': 125,      # -------------------
            'P3': 6700,     # -------------------
            'pulse3': 0.3,  # -     for TSS     -
            'f3': 160,      # -------------------
            'P4': 6700,     # -------------------
            'pulse4': 0.3,  # -   for painted   -
            'f4': 160,      # -------------------
            'P5': 8200,     # -------------------
            'pulse5': 0.4,  # -   for copper    -
            'f5': 109       # -------------------
        }

        # machine settings
        self.settings = self.default_settings.copy()

        # visual options
        sg.SetOptions(
            icon=None,
            button_color=(None, None),
            element_size=(None, None),
            margins=(None, None),
            element_padding=(None, None),
            auto_size_text=None,
            auto_size_buttons=None,
            font=None,
            border_width=None,
            slider_border_width=None,
            slider_relief=None,
            slider_orientation=None,
            autoclose_time=None,
            message_box_line_width=None,
            progress_meter_border_depth=None,
            progress_meter_style=None,
            progress_meter_relief=None,
            progress_meter_color=None,
            progress_meter_size=None,
            text_justification=None,
            background_color=None,
            element_background_color=None,
            text_element_background_color=None,
            input_elements_background_color=None,
            scrollbar_color=None, text_color=None,
            debug_win_size=(None, None),
            window_location=(None, None)
        )

        # define main window layout
        self.layout = [
            # absobrber info
            [sg.Text("Όνομα/Κωδικός/πληροφορίες" + '\n' + "απορροφητή",
             size=(LCOL_WIDTH, 2),
             auto_size_text=False,
             justification='right'),
             sg.Multiline('', do_not_clear=True, size=(25, 3),
                          enable_events=True, key='absorber_info')],

            # absorber drawing number
            [sg.Text("Αριθμός Σχεδίου",
             size=(LCOL_WIDTH, 1),
             auto_size_text=False,
             justification='right'),
             sg.InputText(do_not_clear=True, size=(25, 1),
             enable_events=True, key='drawing_number')],

            # absorber type
            [sg.Text("Τύπος απορροφητή", size=(LCOL_WIDTH, 2),
             auto_size_text=False,
             justification='right'),
             sg.Frame(layout=[
                [sg.Radio("Κατακόρυφος", 'absorber_type_radio',
                 default=True,
                 enable_events=True,
                 key='is_vertical')],
                [sg.Radio("Οριζόντιος", 'absorber_type_radio',
                 enable_events=True,
                 key='is_horizontal')],
                [sg.Radio("Με λωρίδες (φινάκια)", 'absorber_type_radio',
                 enable_events=True,
                 key='is_strips')],
                [sg.Radio("Με μαίανδρο", 'absorber_type_radio',
                 enable_events=True,
                 key='is_meander')]
             ],
                title='',
                relief=sg.RELIEF_FLAT
             )],

            # panel/strips section
            [sg.Frame("Χαρακτηριστικά φύλλου/λωρίδων " + '(mm)', layout=[
                # panel/strips material
                [sg.Text("Υλικό", size=(FRAME_LCOL_WIDTH, 2),
                         auto_size_text=False,
                         justification='right'),
                 sg.Frame('', [
                    [sg.Radio("Επιλεκτικό", 'panel_mat_radio',
                     default=True, key='is_selective')],
                    [sg.Radio("Επιλεκτικό 0.4", 'panel_mat_radio',
                     key='is_selective04')],
                    [sg.Radio('TSS', 'panel_mat_radio',
                     key='is_tss')],
                    [sg.Radio("Βαμμένο", 'panel_mat_radio',
                     key='is_painted')],
                    [sg.Radio("Χαλκός", 'panel_mat_radio',
                     key='is_copper')]
                 ],
                    relief=sg.RELIEF_FLAT
                 )],

                # panel/strips dimensions
                [sg.Text("Μήκος", size=(FRAME_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right',
                 key='panel_length_label'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='panel_length')],

                [sg.Text("Πλάτος", size=(FRAME_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right',
                 key='panel_width_label'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='panel_width')],

                # [sg.Text("Αριθμός", size=(FRAME_LCOL_WIDTH, 1),
                #  auto_size_text=False,
                #  justification='right', text_color='gray',
                #  key='strip_count_label'),
                #  sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                #  key='strip_count', enable_events=True, disabled=True)],

                [sg.Text('', size=(FRAME_LCOL_WIDTH, 1)),
                 sg.Checkbox("Οπές στις γωνίες",
                 default=False,
                 key='panel_holes')]
             ]),

             # grid section
             sg.Frame("Χαρακτηριστικά " + 'grid' + " σωληνών " + '(mm)',
                 layout=[
                # header diameter
                [sg.Text("Φ" + ' header', size=(FRAME2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('22', do_not_clear=True, size=(TB_WID, 1),
                 key='header_diameter')],

                # riser diameter
                [sg.Text("Φ" + ' riser', size=(FRAME2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('8', do_not_clear=True, size=(TB_WID, 1),
                 key='riser_diameter')],

                # head to head distance
                [sg.Text("Κέντρο-κέντρο", size=(FRAME2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='head_to_head')],

                # free header exit length
                [sg.Text("Μήκος ελεύθερης" + '\n' + "εξόδου "+ 'header',
                 size=(FRAME2_LCOL_WIDTH, 2),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='header_exit_length')],

                # header total length
                [sg.Text("Μήκος " + 'header\n' + "με κλειστή έξοδο",
                 size=(FRAME2_LCOL_WIDTH, 2),
                 auto_size_text=False,
                 justification='right', text_color='gray',
                 key='header_length_label'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='header_length', disabled=True)],

                # closed exits
                [sg.Text('', size=(int(FRAME2_LCOL_WIDTH/2-2), 1)),
                 sg.Frame("Κλειστές έξοδοι", [
                    [sg.Checkbox('', default=False,
                     enable_events=True,
                     key='up_left_exit_closed'),
                     sg.Checkbox('', default=False,
                     enable_events=True,
                     key='up_right_exit_closed')],
                    [sg.Checkbox('', default=False,
                     enable_events=True,
                     key='down_left_exit_closed'),
                     sg.Checkbox('', default=False,
                     enable_events=True,
                     key='down_right_exit_closed')]
                 ])],

                # distance of 1st riser from edge
                [sg.Text("Απόσταση α" + '\' riser\n'+" από άκρη φύλλου",
                 size=(FRAME2_LCOL_WIDTH, 2),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='riser_edge_distance')],

                # riser step
                [sg.Text("Βήμα " + 'riser', size=(FRAME2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='riser_step')],

                # riser count
                [sg.Text("Αριθμός "+'riser', size=(FRAME2_LCOL_WIDTH,1),
                 auto_size_text=False,
                 justification='right', key='riser_count_label'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='riser_count', enable_events=True)],

                # riser count
                [sg.Text("Πλάτος μαιάνδρου", size=(FRAME2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right', text_color='gray',
                 key='meander_width_label'),
                 sg.InputText(do_not_clear=True, size=(TB_WID, 1),
                 key='meander_width', disabled=True)],
             ])],

            # error box
            [sg.Text('', text_color='red', size=(60, 2),
                     key='error_box')],

            # buttons
            [sg.Text(' ' * 35),
             sg.Button("Δημιουργία", size=(10, 1), key='save_button'),
             sg.Button("Έξοδος", size=(10, 1), key='exit_button'),
             sg.Text(' ' * 12),
             sg.Button("Ρυθμίσεις" + '\n' + "μηχανής", size=(8, 2),
                       key='settings_button')]
        ]

        # define machine settings window layout
        self.settings_layout = [
            [sg.Frame('', layout=[
                [sg.Text('Vel', size=(SETTINGS2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='vel')],
                [sg.Text('Acc', size=(SETTINGS2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='acc')],
                [sg.Text('Pres', size=(SETTINGS2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='pres')],
                [sg.Text('Z', size=(SETTINGS2_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='Z')]
             ]),
             sg.Frame('', layout=[
                [sg.Text('Power (W)', size=(SETTINGS_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='P')],
                [sg.Text('Pulse (ms)', size=(SETTINGS_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='pulse')],
                [sg.Text('Freq (Hz)', size=(SETTINGS_LCOL_WIDTH, 1),
                 auto_size_text=False,
                 justification='right'),
                 sg.InputText('', do_not_clear=True, size=(6, 1),
                 enable_events=True,
                 key='f')]
             ])],

            # error box
            [sg.Text('', text_color='red', size=(35, 2),
                     key='settings_error_box')],

            # buttons
            [sg.Button('OK', size=(10, 1),
                       key='OK_button'),
             sg.Button("Αποθήκευση", size=(10, 1),
                       key='export_button'),
             sg.Button("Επαναφορά", size=(10, 1),
                       key='reset_button')]
        ]

        # drawing instance
        self.drawing = Drawing()

        # file manager instance
        self.file_manager = FileManager()

    def set_to_strips(self):
        # (self.window.Element('strip_count_label')
        #  .Update(text_color='black'))
        # self.window.Element('strip_count').Update(disabled=False)
        self.window.Element('panel_holes').Update(disabled=True)
        self.window.Element('is_selective').Update(value=True)
        self.window.Element('is_tss').Update(disabled=True)
        self.window.Element('is_painted').Update(disabled=True)
        self.window.Element('is_copper').Update(disabled=True)

    def set_to_panel(self):
        # (self.window.Element('strip_count_label')
        #  .Update(text_color='gray'))
        # self.window.Element('strip_count').Update(disabled=True)
        self.window.Element('panel_holes').Update(disabled=False)
        self.window.Element('is_tss').Update(disabled=False)
        self.window.Element('is_painted').Update(disabled=False)
        self.window.Element('is_copper').Update(disabled=False)

    def set_to_meander(self):
        (self.window.Element('meander_width_label')
         .Update(text_color='black'))
        self.window.Element('meander_width').Update(disabled=False)

    def unset_to_meander(self):
        (self.window.Element('meander_width_label')
         .Update(text_color='gray'))
        self.window.Element('meander_width').Update(disabled=True)

    def reset_grid(self, is_horizontal):
        # if needed clear grid
        if is_horizontal != self.was_horizontal:
            self.clear_grid()
        self.was_horizontal = is_horizontal

    def clear_grid(self):
        self.window.Element('header_diameter').Update('22')
        self.window.Element('riser_diameter').Update('8')
        self.window.Element('head_to_head').Update('')
        self.window.Element('header_exit_length').Update('')
        self.window.Element('riser_edge_distance').Update('')
        self.window.Element('riser_step').Update('')
        (self.window.Element('up_left_exit_closed')
         .Update(False, disabled=False))
        (self.window.Element('up_right_exit_closed')
         .Update(False, disabled=False))
        (self.window.Element('down_left_exit_closed')
         .Update(False, disabled=False))
        (self.window.Element('down_right_exit_closed')
         .Update(False, disabled=False))

        (self.window.Element('header_length_label')
         .Update(text_color='gray'))
        (self.window.Element('header_length')
         .Update(disabled=True))

    def set_exits(self, values):
        is_horizontal = values['is_horizontal']
        if not is_horizontal:
            # allow only one of up exits closed
            if values['up_left_exit_closed']:
                (self.window.Element('up_right_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('up_right_exit_closed').
                 Update(disabled=False))

            if values['up_right_exit_closed']:
                (self.window.Element('up_left_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('up_left_exit_closed').
                 Update(disabled=False))

            # allow only one of down exits closed
            if values['down_left_exit_closed']:
                (self.window.Element('down_right_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('down_right_exit_closed').
                 Update(disabled=False))

            if values['down_right_exit_closed']:
                (self.window.Element('down_left_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('down_left_exit_closed').
                 Update(disabled=False))
        else:
            # allow only one of left exits closed
            if values['up_left_exit_closed']:
                (self.window.Element('down_left_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('down_left_exit_closed').
                 Update(disabled=False))

            if values['down_left_exit_closed']:
                (self.window.Element('up_left_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('up_left_exit_closed').
                 Update(disabled=False))

            # allow only one of right exits closed
            if values['up_right_exit_closed']:
                (self.window.Element('down_right_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('down_right_exit_closed').
                 Update(disabled=False))

            if values['down_right_exit_closed']:
                (self.window.Element('up_right_exit_closed').
                 Update(disabled=True))
            else:
                (self.window.Element('up_right_exit_closed').
                 Update(disabled=False))

        # disable/enable header length text box
        if True in (values['up_left_exit_closed'],
                    values['up_right_exit_closed'],
                    values['down_left_exit_closed'],
                    values['down_right_exit_closed']):
            (self.window.Element('header_length_label')
             .Update(text_color='black'))
            (self.window.Element('header_length')
             .Update(disabled=False))
        else:
            (self.window.Element('header_length_label')
             .Update(text_color='gray'))
            (self.window.Element('header_length')
             .Update(disabled=True))

    def is_float(self, string):
        try:
            if float(string) > 0.0:
                return True
            else:
                return False
        except ValueError:
            return False

    def check_for_errors(self, values):
        # check for positive floats
        try:
            for key in values.keys():
                # skip absorber info
                if key in ('absorber_info', 'drawing_number'):
                    continue

                # skip disabled values for each casa
                if not values['is_strips']:
                    if key == 'strip_count':
                        continue
                if not values['is_meander']:
                    if key == 'meander_width':
                        continue
                if True not in (values['up_left_exit_closed'],
                                values['up_right_exit_closed'],
                                values['down_left_exit_closed'],
                                values['down_right_exit_closed']):
                    if key == 'header_length':
                        continue

                if type(values[key]) == str:
                    if not self.is_float(values[key]):
                        return "Σφάλμα: επιτρέπονται μόνο θετικοί αριθμοί"
        except AttributeError:
            return "Σφαλμα: μη έγκυρη τιμή"

        # check head-to-head+header diameter and panel width or length
        if values['is_horizontal']:
            if (values['head_to_head'] + values['header_diameter'] >
               values['panel_width']):
                return ("Σφάλμα: το πλάτος του φύλλου δεν καλύπτει "
                        "πλήρως τους headers")
        else:
            if (values['head_to_head'] + values['header_diameter'] >
               values['panel_length']):
                return ("Σφάλμα: το μήκος του φύλλου δεν καλύπτει "
                        "πλήρως τους headers")

        # check tube diameters
        if values['riser_diameter'] > values['header_diameter']:
            return ("Σφαλμα: η διάμετρος των " + 'riser' +
                    "δεν μπορεί να είναι μεγαλύτερη από αυτή των " + 
                    'header')

        # check riser step and riser diameter
        if values['riser_step'] < values['riser_diameter']:
            return ("Σφαλμα: το βήμα των " + 'riser' + " δεν μπορεί " +
                    "να είναι μικρότερο από τη διάμετρό τους")

        # check riser step and panel length or width
        if values['is_horizontal'] or values['is_meander']:
            if values['riser_step'] > values['panel_length']:
                return ("Σφαλμα: το βήμα των " + 'riser' +
                        " δεν μπορεί να είναι μεγαλύτερο από το " +
                        "μήκος του " + '\n' + "φύλλου (σε "
                        "οριζόντιο απορροφητή ή μαίανδρο)")
        else:
            if values['riser_step'] > values['panel_width']:
                return ("Σφαλμα: το βήμα των " + 'riser' +
                        " δεν μπορεί να είναι μεγαλύτερο από το " +
                        "συνολκό πλάτος του" + '\n' + "φύλλου")

        # check riser edge distance and panel width or length
        if values['is_horizontal']:
            if values['riser_edge_distance'] > values['panel_length']:
                return ("Σφαλμα: η απόσταση α" + '\'' +
                        " από την άκρη του φύλλου "
                        "δεν μπορεί να είναι μεγαλύτερη " + '\n' +
                        "από το μήκος του φύλλου (σε οριζόντιο " + 
                        "απορροφητή)")
        else:
            if values['riser_edge_distance'] > values['panel_width']:
                return ("Σφαλμα: η απόσταση α" + '\'' +
                        " από την άκρη του φύλλου "
                        "δεν μπορεί να είναι μεγαλύτερη " + '\n' +
                        "από το συνολικό πλάτος των φύλλων")

        # check header length and free exit length
        if True in (values['up_left_exit_closed'],
                    values['up_right_exit_closed'],
                    values['down_left_exit_closed'],
                    values['down_right_exit_closed']):
            if values['header_length'] < values['header_exit_length']:
                return ("Σφαλμα: το μήκος της ελεύθερης εξόδου δεν "
                        "μπορεί να έιναι μεγαλύτερο από το " + '\n' +
                        "μήκος του " + 'header')

        # check for floating risers
        if values['is_horizontal'] or values['is_meander']:
            if ((values['riser_count']-1)*values['riser_step'] +
               values['riser_edge_distance'] > values['panel_length']):
                return ("Σφαλμα: δεν χωράει τόσο μεγάλος αριθμός "
                        "riser στο μήκος του φύλλου")
        else:
            if ((values['riser_count']-1)*values['riser_step'] +
               values['riser_edge_distance'] > values['panel_width']):
                return ("Σφαλμα: δεν χωράει τόσο μεγάλος αριθμός "
                        "riser στο πλατος του φύλλου")

        # check for meander width and panel width
        if values['is_meander']:
            if (values['riser_edge_distance'] + values['meander_width'] >
               values['panel_width']):
                return ("Σφάλμα: ο μαίανδρος " + 'riser' +
                        " είναι μεγαλύτερος σε πλάτος από το φύλλο")

        return ''

    def check_settings_for_errors(self, values):
        # check for positive floats
        try:
            for key in values.keys():
                if type(values[key]) == str:
                    if not self.is_float(values[key]):
                        return "Σφάλμα: επιτρέπονται μόνο θετικοί αριθμοί"
        except AttributeError:
            return "Σφαλμα: μη έγκυρη τιμή"

        return ''

    def show_error(self, error):
        self.window.Element('error_box').Update(error)

    def show_settings_error(self, error):
        self.settings_window.Element('settings_error_box').Update(error)

    def export_settings_to_file(self):
        with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as the_file:
            for key in self.settings.keys():
                # write separators
                if key == 'Z1':
                    the_file.write(
                        ('\n# Z' + " για " + 'riser' +
                            " Φ8 ή μικρότερους" + '\n')
                    )
                elif key == 'Z2':
                    the_file.write(
                        ('\n# Z' + " για " + 'riser' +
                            "μεγαλύτερους από Φ8" + '\n')
                    )
                elif key == 'P1':
                    the_file.write(
                        '\n#'+" ρυθμίσεις για επιλεκτικά φύλλα"+'\n'
                    )
                elif key == 'P2':
                    the_file.write(
                        ('\n#' + " ρυθμίσεις για επιλεκτικά φύλλα με " +
                            '0.4\n')
                    )
                elif key == 'P3':
                    the_file.write(
                        ('\n#' + " ρυθμίσεις για "+'TSS'+" φύλλα" + '\n'
                    )
                elif key == 'P4':
                    the_file.write(
                        '\n#' + " ρυθμίσεις για βαμμένα φύλλα" + '\n'
                    )
                elif key == 'P5':
                    the_file.write(
                        '\n#' + " ρυθμίσεις για φύλλα από χαλκό" + '\n'
                    )
                the_file.write(key+'=' + str(self.settings[key]) + '\n')

    def import_settings_from_file(self):
        # reset imported settings to defaults
        imported_settings = self.default_settings.copy()

        # if custom settings file is present in current directory then
        # import these settings
        if self.SETTINGS_FILE_EXISTS:
            with open(self.SETTINGS_FILE, encoding='utf-8') as the_file:
                for line in the_file:
                    # skip comment lines
                    if line.startswith('#'):
                        continue
                    # store appropriate
                    for key in self.settings.keys():
                        if line.startswith(key + '='):
                            imported_settings[key] = (line.strip('\n')
                                                      .split('=')[1])

        return imported_settings

    def fill_settings_window(self, main_values):
        # print loaded settings file
        if self.SETTINGS_FILE_EXISTS:
            self.show_settings_error(
                ("Οι αρχικές ρυθμίσεις φορτώθηκαν από το αρχείο:"+'\n' +
                 self.SETTINGS_FILE)
            )

        for item in ('vel', 'acc', 'pres'):
            self.settings_window.Element(item).Update(self.settings[item])

        # set Z depending on riser diameter
        if main_values['riser_diameter'] == '':
            main_values['riser_diameter'] = 0
        if main_values['riser_diameter'] <= 8:
            self.settings_window.Element('Z').Update(self.settings['Z1'])
        else:
            self.settings_window.Element('Z').Update(self.settings['Z2'])

        # set laser parameters according to panel material
        if main_values['is_selective']:
            for item in ('P', 'pulse', 'f'):
                (self.settings_window.Element(item)
                 .Update(self.settings[item + '1']))
        elif main_values['is_selective04']:
            for item in ('P', 'pulse', 'f'):
                (self.settings_window.Element(item)
                 .Update(self.settings[item + '2']))
        elif main_values['is_tss']:
            for item in ('P', 'pulse', 'f'):
                (self.settings_window.Element(item)
                 .Update(self.settings[item + '3']))
        elif main_values['is_painted']:
            for item in ('P', 'pulse', 'f'):
                (self.settings_window.Element(item)
                 .Update(self.settings[item + '4']))
        elif main_values['is_copper']:
            for item in ('P', 'pulse', 'f'):
                (self.settings_window.Element(item)
                 .Update(self.settings[item + '5']))

    def run_settings(self, main_values):
        # draw settings window
        self.settings_window = (sg.Window("Ρυθμίσεις Μηχανής",
                                keep_on_top=True)
                                .Layout(self.settings_layout))
        self.settings_window.Finalize()

        self.fill_settings_window(main_values)

        # settings window event Loop
        while True:
            # get the event and current values
            event, values = self.settings_window.Read()

            # user closes the window
            if event in (None, 'OK_button'):
                break

            # format values
            for key, val in values.items():
                if self.is_float(val):
                    values[key] = float(val)

            # check for errors in any event except 'reset', 'X', or 'OK'
            if event not in (None, 'OK_button', 'reset_button'):
                self.show_settings_error('')
                error_found = self.check_settings_for_errors(values)
                if error_found != '':
                    self.show_settings_error(error_found)
                    continue

            # user presses 'export settings file' button
            if event == 'export_button':
                self.export_settings_to_file()

                self.show_settings_error(
                    ("Οι ρυθμίσεις αποθηκεύτηκαν στο αρχείο:" + '\n' +
                     self.SETTINGS_FILE)
                )

            # user presses 'reset' button
            if event == 'reset_button':
                self.settings = self.default_settings.copy()
                self.fill_settings_window(main_values)

                loaded_from = ''
                if self.SETTINGS_FILE_EXISTS:
                    loaded_from = " από:" + '\n' + self.SETTINGS_FILE

                self.show_settings_error(
                    ("Οι ρυθμήσεις επαναφέρθηκαν στις αρχικές" +
                     loaded_from)
                )

            # if user modifies a value then store it
            if event in ('vel', 'acc', 'pres'):
                self.settings[event] = values[event]

            if event == 'Z':
                if main_values['riser_diameter'] <= 8:
                    self.settings['Z1'] = values['Z']
                else:
                    self.settings['Z2'] = values['Z']

            if event in ('P', 'pulse', 'f'):
                if main_values['is_selective']:
                    self.settings[event + '1'] = values[event]
                elif main_values['is_selective04']:
                    self.settings[event + '2'] = values[event]
                elif main_values['is_painted']:
                    self.settings[event + '3'] = values[event]
                elif main_values['is_copper']:
                    self.settings[event + '4'] = values[event]

            # DEBUG
            # print('\nsettings event: ')
            # pprint(event)
            # print('\nsettings values: ')
            # pprint(values)

        self.settings_window.Close()

    def run(self):
        # draw main window
        self.window = (sg.Window("Δημιουργία Εντολής Εργασίας")
                       .Layout(self.layout))

        # initialize machine settings
        self.default_settings = self.import_settings_from_file()
        self.settings = self.default_settings.copy()

        # main window vent Loop
        while True:
            # get the event and current values
            event, values = self.window.Read()

            # user closes the window
            if event in (None, 'exit_button'):
                break

            # format values
            for key, val in values.items():
                if key in ('absorber_info', 'drawing_number'):
                    continue
                if self.is_float(val):
                    if key in ('strip_count', 'riser_count'):
                        values[key] = int(float(val))
                    elif 'closed' in key:
                        values[key] = bool(int(val))
                    else:
                        values[key] = float(val)

            # user presses 'save' button
            if event == 'save_button':
                # print errors (if any)
                self.show_error('')
                error_found = self.check_for_errors(values)
                if error_found != '':
                    self.show_error(error_found)
                    continue

                # disable buttons
                self.window.Element('save_button').Update(disabled=True)
                self.window.Element('exit_button').Update(disabled=True)
                (self.window.Element('settings_button')
                 .Update(disabled=True))

                # prompt user to supply file name
                self.output_file = sg.PopupGetFile(
                    title="Αποθήκευση αρχείου",
                    message=("Παρακαλώ εισάγετε την τοποθεσία του "
                             "παραγόμενου αρχείου"),
                    save_as=True,
                    default_path=(self.default_output_folder +
                                  self.guessed_name + '.pdf'),
                    default_extension='pdf',
                    file_types=(("PDF", "*.pdf"),)
                )

                # if a name is defined then proceed to save
                if self.output_file:
                    # ensure correct file extension
                    if not self.output_file.endswith('.pdf'):
                        self.output_file += '.pdf'

                    # clean up save directory
                    files_were_moved = self.file_manager.prepare_dir(
                        values['drawing_number'],
                        path.dirname(self.output_file), self.OLDS_DIR)

                    if files_were_moved:
                        moved_files_message = ''

                    # create job order PDF
                    self.drawing = Drawing()
                    self.drawing.make_job_order(self.output_file, values,
                                                self.settings)

                    self.show_error(("Το αρχέιο αποθηκεύτηκε στην "
                                     "τοποθεσία:" + '\n' +
                                     self.output_file))

                # re-enable buttons
                self.window.Element('save_button').Update(disabled=False)
                self.window.Element('exit_button').Update(disabled=False)
                (self.window.Element('settings_button')
                 .Update(disabled=False))

            # user presses 'machine settings' button
            if event == 'settings_button':
                # print errors (if any)
                # self.show_error('')
                # error_found = self.check_for_errors(values)
                # if error_found != '':
                #     self.show_error(error_found)
                #     continue

                # disable buttons
                self.window.Element('save_button').Update(disabled=True)
                self.window.Element('exit_button').Update(disabled=True)
                (self.window.Element('settings_button')
                 .Update(disabled=True))

                # open machine settings window
                self.run_settings(values)

                # re-enable buttons
                self.window.Element('save_button').Update(disabled=False)
                self.window.Element('exit_button').Update(disabled=False)
                (self.window.Element('settings_button')
                 .Update(disabled=False))

            # update panel and grid on product type change
            if event in ('is_vertical', 'is_horizontal', 'is_strips',
                         'is_meander'):
                self.reset_grid(values['is_horizontal'])

                if event == 'is_meander':
                    self.set_to_meander()
                else:
                    self.unset_to_meander()

                if event == 'is_strips':
                    self.set_to_strips()
                else:
                    self.set_to_panel()

            # set exits
            if event in ('up_left_exit_closed',
                         'up_right_exit_closed',
                         'down_left_exit_closed',
                         'down_right_exit_closed'):
                self.set_exits(values)

            # force integers in 'strip count' field
            if event in ('strip_count', 'riser_count'):
                if isinstance(values[event], str):
                    cur_value = values[event].replace(',', '.')
                    if self.is_float(cur_value):
                        self.window.Element(event).Update(
                            (str(int(float(cur_value)))))
                else:
                    self.window.Element(event).Update(int(values[event]))

            # set possible file name and set panel material
            if event in ('absorber_info', 'drawing_number'):
                # format name
                guessed_name = (values['absorber_info']
                                .split('\n')[0]
                                .strip(',|.| |\t'))

                # format guessed name and drawing number
                for char in ['/', '\\', '|', '*']:
                    guessed_name = guessed_name.replace(char, '-')
                    values['drawing_number'] = (values['drawing_number']
                                                .replace(char, '-'))

                for char in ['\t', ':', '?', '<', '>']:
                    guessed_name = guessed_name.replace(char, '')
                    values['drawing_number'] = (values['drawing_number']
                                                .replace(char, ''))

                self.window.Element('drawing_number').Update(
                    values['drawing_number'])

                # append drawing number, if any
                if values['drawing_number'] != '':
                    guessed_name = (values['drawing_number'] + '-' +
                                    guessed_name)

                if guessed_name != '':
                    self.guessed_name = guessed_name

                # set panel material
                if re.search('.*FP[0-9]{4}$', guessed_name):
                    product_series = guessed_name[-4]

                    if product_series == '8':  # check if strips
                        (self.window.Element('is_strips')
                         .Update(value=True))
                        self.set_to_strips()
                        self.reset_grid(is_horizontal=False)
                    else:
                        # if is already strips then set to vertical
                        if values['is_strips']:
                            (self.window.Element('is_vertical')
                             .Update(value=True))
                            self.set_to_panel()
                            self.reset_grid(is_horizontal=False)

                        if product_series == '2':  # check if selective
                            (self.window.Element('is_selective')
                             .Update(value=True))
                        elif product_series == '3':  # check if TSS
                            (self.window.Element('is_tss')
                             .Update(value=True))
                        elif product_series == '4':  # check if painted
                            (self.window.Element('is_painted')
                             .Update(value=True))

            # DEBUG
            # print('\nevent: ')
            # pprint(event)
            # print('\nvalues: ')
            # pprint(values)

        self.window.Close()
