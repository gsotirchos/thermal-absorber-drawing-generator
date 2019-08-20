from os import path, listdir, mkdir, rename
# from pprint import pprint


class FileManager:
    def __init__(self):
        self.drawing_number = '0000'
        self.dir_path = 'drawing_no-product_name.pdf'
        self.OLDS_DIR_NAME = 'old'

    def current_drawings(self, drawing_number, dir_path):
        cur_drawings = []
        if drawing_number == '':
            return cur_drawings
        for file_name in listdir(dir_path):
            if file_name.startswith(drawing_number):
                cur_drawings.append(file_name)
        return cur_drawings

    def move_file(self, file_name, old_dir, new_dir):
        # determine appropriate file name
        new_file_name = file_name
        count = 1
        name, extension = path.splitext(file_name)
        while path.isfile(path.join(new_dir, new_file_name)):
            count += 1
            new_file_name = name + ' (' + str(count) + ')' + extension

        # move the file
        old_file_path = path.join(old_dir, file_name)
        new_file_path = path.join(new_dir, new_file_name)
        rename(old_file_path, new_file_path)

    def prepare_dir(self, drawing_number, dir_path, olds_dir_name):
        # store any existing file names with same drawing number
        cur_drawings = self.current_drawings(drawing_number, dir_path)
        if cur_drawings:
            # if olds directory doesn't exist, create it
            olds_dir_path = dir_path + '\\' + olds_dir_name
            if not path.isdir(olds_dir_path):
                mkdir(olds_dir_path)

            old_drawings_path = olds_dir_path + '\\' + drawing_number
            if not path.isdir(old_drawings_path):
                mkdir(old_drawings_path)

            # move every existing drawing to olds dir without overwriting
            for drawing in cur_drawings:
                self.move_file(drawing, dir_path, old_drawings_path)

            files_were_found = True
        else:
            files_were_found = False

        return files_were_found
