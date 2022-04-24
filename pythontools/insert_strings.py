import os, sys
from pathlib import Path
import csv
from shutil import copyfile

def insert_strings(csv_file_path, file_type):
    with open(Path("pythontools/temp/phase.txt")) as phase_file:
        if phase_file.readline() != 'insert':
            raise Exception("phase needs to be insert phase!")

    with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        is_first = True

        rows = []

        for row in csv_reader:
            if is_first:
                is_first = False
                continue
            row.append(False)
            rows.append(row)

    # array is in this format: ['text_title', 'address', 'text', 'file_name', 'file_type', 'unused', 'translation', 'credit', 'notes', **'already_read'] **This is not part of the original csv file, but something added to batch rows from the same files together and ensure that no file is read twice.

    if file_type == "inc_file":

        copied_files = []

        for row in rows:
            already_read = row[9]
            if already_read:
                continue
            
            # get rows from the same file
            same_file_rows = {}
            file_name = row[3]
            for row_ in rows:
                already_read = row_[9]
                if already_read:
                    continue
                if row_[3] == file_name:
                    same_file_rows[row_[0]] = row_

            insert_file_path = Path(file_name)

            with open(insert_file_path, encoding='utf-8') as file:
                data = file.readlines()

            i = 0 # should correspond with data file
            # go through the data
            skip_insert = True

            copied_data = data.copy()
            for line in copied_data:
                # TODO: once non-string parts are marked, ADD A WAY TO SKIP OVER THEM AND somehow NOTIFY THEM FOR MANUAL INSERTION
                if line == '\n': # i.e., the line is empty, except for the end.
                    pass
                elif line[0] in '.#@': # the line is likely a command or a comment, and therefore should not be modified
                    pass
                elif line[:8] == "\t.string" or line[:11] == "    .string":
                    # delete these lines, and replace with the translation
                    if not skip_insert: # if there isn't anything in translation, then skip it.
                        if len(translation_lines) > 0:
                            data[i] = '\t.string "' + translation_lines.pop(0).strip() + '"\n'
                        else:
                            data.pop(i) # removes value from list
                            i -= 1 # corrects index so that the index will still correspond to data list
                else: # the method name and address line
                    try:
                        row_ = same_file_rows[line.split(":")[0]] # gives the string until the first ':' character
                    except KeyError:
                        i += 1
                        skip_insert = True
                        continue
                    
                    row_[9] = True # mark as already read

                    text_title = row_[0]
                    address = row_[1]
                    text = row_[2]
                    file_name = row_[3]
                    unused = row_[5]
                    translation = row_[6]
                    credit = row_[7]
                    notes = row_[8]

                    skip_insert = translation == ''
                    if not skip_insert:
                        print(["translation: " + translation])

                    translation_lines = translation.split("\n")
                i += 1 
            
            if data != copied_data: # i.e. if some change occured, then make a copy and write the result to file. copied_data reflects the original, pre-modified data

                copyfile(insert_file_path, insert_file_path.with_stem(insert_file_path.stem + "_tEmP")) # copies original file to its original name and _tEmP; e.g. abnormal_weather.inc --> abnormal_weather_tEmP.inc. The temp file will be a carbon copy of the original, and the original will be modified; after the modification, a separate program should be run to revert the temp file back as a regular file.

                copied_files.append(insert_file_path)
                
                with open(insert_file_path, "w", encoding='utf-8') as file:
                    file.writelines(data)
    
    with open(Path("pythontools/temp/temp.txt").with_stem(csv_file_path.stem + "_tEmP"), "w") as temp_file:
        temp_file.writelines([str(file) + "\n" for file in copied_files])

    with open(Path("pythontools/temp/phase.txt"), 'w') as phase_file:
        phase_file.write("cleanup")
            
def clean_up(csv_file_path): #removes the _tEmP files
    with open(Path("pythontools/temp/phase.txt")) as phase_file:
        if phase_file.readline() != 'cleanup':
            raise Exception("phase needs to be cleanup phase!")

    with open(Path("pythontools/temp/temp.txt").with_stem(csv_file_path.stem + "_tEmP")) as temp_file:
        copied_files = temp_file.readlines()

    for file_path in copied_files:
        file = Path(file_path.strip())
        copyfile(file.with_stem(file.stem + "_tEmP"), file)
        os.remove(file.with_stem(file.stem + "_tEmP"))

    with open(Path("pythontools/temp/phase.txt"), 'w') as phase_file:
        phase_file.write("insert")


if __name__ == "__main__":
    filepath = Path(sys.argv[2])
    if sys.argv[1] == "insert":
        insert_strings(filepath, "inc_file")
    elif sys.argv[1] == "cleanup":
        clean_up(filepath)
    else:
        print("Syntax is python insert_strings.py insert|cleanup csv_filepath")