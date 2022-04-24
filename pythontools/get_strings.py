import os
from pathlib import Path
from copy import copy, deepcopy

class TextToTranslate:
    def __init__(self, text_title="", text_inside="", address="", file_path=None, file_type="", unused=False):
        self.text_title, self.text_inside, self.address, self.file_path, self.file_type, self.unused = text_title, text_inside, address, file_path, file_type, unused

    def append_text_inside(self, string):
        self.text_inside += string
    
    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, file_path=self.file_path, file_type=self.file_type, unused=self.unused)

    def write_csv(self, file):
        file.write('"' + self.text_title + '","' + self.address + '","' + self.text_inside + '","' + str(self.file_path)+ '","' + self.file_type + '","' + str(self.unused) +'"\r')

    def get_csv_init(self, file):
        file.write("text_title,address,text,file_name,file_type,unused\r")

class StringToTranslate(TextToTranslate):
    def __init__(self, text_title="", text_inside="", address="", file_path=None, file_type="", unused=False, aligned4=False):
        super().__init__(text_title, text_inside, address, file_path, file_type, unused)
        self.aligned4 = aligned4
    
    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, unused=self.unused, aligned4=self.aligned4)

    def write_csv(self, file):
        file.write('"' + self.text_title + '","' + self.address + '","' + self.text_inside + '","' + str(self.file_path)+ '","' + self.file_type + '","' + str(self.unused) +'","' + str(self.aligned4) + '"\r')
    
    def get_csv_init(self, file):
        file.write("text_title,address,text,file_name,file_type,unused,aligned4\r")

class BattleStringToTranslate(TextToTranslate):
    def __init__(self, text_title="", text_inside="", address="", file_path=None, file_type="", unused=False, static=False):
        super().__init__(text_title, text_inside, address, file_path, file_type, unused)
        self.static = static

    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, unused=self.unused, static=self.static)

    def write_csv(self, file):
        file.write('"' + self.text_title + '","' + self.address + '","' + self.text_inside + '","' + str(self.file_path)+ '","' + self.file_type + '","' + str(self.unused) +'","' + str(self.static) + '"\r')

    def get_csv_init(self, file):
        file.write("text_title,address,text,file_name,file_type,unused,static\r")


def scrape_file(file_path, csv_file, file_type):

    with file_path.open(encoding='utf-8') as file:
        # text for the whole file
        to_translate_texts = []
        isFirst = True

        # actual code         
        if file_type == "inc_file":
            next_is_unused = False # if the line says @ Unused, then the NEXT line will be the header of the unused line.
            has_string_literal = False
            while True:
                # print(text_titles, text_insides, addresses)
                line = file.readline()
                # print(line)
                # breaks if the line is None
                if not line:
                    if has_string_literal:
                        to_translate_texts.append(copy(dialog_box))
                    break
                
                # if it doesn't start with a '\t' character, it's a new line or a new header
                if line == '\n': # i.e., the line is empty, except for the end.
                    pass
                elif line[0] == '.' or line[0] == '#': # the line is likely a command, and therefore should not be counted
                    pass
                elif line[0] == '\t':
                    # starts with '\t.string "'
                    if isFirst: # if there's anything that's written before the first text title and address, ignore it.
                        continue
                    if '.string "' not in line: # if the line starts with a tab but does not have a ".string" tag, continue
                    # TODO: mark non-string tags as requiring manual input for translation!
                        continue
                    else:
                        has_string_literal = True
                        dialog_box.append_text_inside(line[10:-2] + "\n") # this \n is not the 'official' line break found inside the actual game text itself
                elif line[0:4] == "    ":
                    # same as above, except indices have to be modified
                    if isFirst:
                        continue
                    if '.string "' not in line:
                        continue
                    else:
                        has_string_literal = True
                        dialog_box.append_text_inside(line[13:-2] +"\n")
                elif line[0] == '@':
                    # starts with '@', which starts all comments
                    next_is_unused = line[1:].lower().strip() == "unused" or line[1:8].lower().strip() == "unused"
                else: # every file should start with this type of line
                    # gives us the text title and address
                    # this also means that a new line is being formed; this will be a surer way to tell when a new section is being formed
                    if isFirst:
                        isFirst = False
                    elif has_string_literal: # if there is a string literal, then add it; if not, don't, and continue on.
                        to_translate_texts.append(copy(dialog_box))
                        has_string_literal = False # reset this for the next iteration 
                    text_title = line.split(":")[0] # gives the string until the first ':' character
                    address = ""
                    if len(line.split("@")) > 1:
                        address = line.split("@")[1].strip() # gives the string after the first "@" character.
                    dialog_box = TextToTranslate(text_title=text_title, text_inside="", address=address, file_path=file_path, file_type=file_type, unused=next_is_unused)
                    next_is_unused = False
                    # print(file_path, file_type)
                    # for the first name and address line, you don't want the system to record the text (there is no text yet)        
        if file_type == "u8_string":
            while True:
                line = file.readline()
                if not line:
                    break
                if line[:9] == "const u8 ":
                    if line[9] == "*": # const u8 * are usually arrays and need not be scraped
                        continue
                    text_title = line.split("[")[0][9:] # gives the string from the first character after 'const u8' until the first "[" character
                    text_inside = line.split('"')[1] # gives the text in between the quotation marks
                    if len(line.split('//')) > 1:
                        unused = line.split("//")[1].lower().strip() == "unused" # if the string ends in // unused
                    else:
                        unused = False
                    aligned4 = False
                    to_translate_texts.append(StringToTranslate(text_title=text_title, text_inside=text_inside, file_path=file_path, file_type=file_type, unused=unused, aligned4=aligned4)) 
                elif line[:20] == "ALIGNED(4) const u8 ":
                    # same as above
                    if line[20] == "*":
                        continue
                    text_title = line.split("[")[0][20:]
                    text_inside = line.split('"')[1]
                    if len(line.split('//')) > 1:
                        unused = line.split("//")[1].lower().strip() == "unused" # if the string ends in // unused
                    else:
                        unused = False
                    aligned4 = True
                    to_translate_texts.append(StringToTranslate(text_title=text_title, text_inside=text_inside, file_path=file_path, file_type=file_type, unused=unused, aligned4=aligned4)) 
        if file_type == "battle_string":
            while True:
                line = file.readline()
                if not line:
                    break
                if '"' not in line: # this means that the line itself doesn't have a quote corresponding to it. Most likely the variable is being instantiated before it actually will get a value.
                    continue
                if line[:9] == "const u8 ":
                    # same as above, except with static instead of aligned4 as the boolean variable
                    if line[9] == "*": # const u8 * are usually arrays and need not be scraped
                        continue
                    text_title = line.split("[")[0][9:] # gives the string from the first character after 'const u8' until the first "[" character
                    text_inside = line.split('"')[1] # gives the text in between the quotation marks
                    # print(text_inside)
                    if len(line.split('//')) > 1:
                        unused = line.split("//")[1].lower().strip() == "unused" # if the string ends in // unused
                    else:
                        unused = False
                    to_translate_texts.append(BattleStringToTranslate(text_title=text_title, text_inside=text_inside, file_path=file_path, file_type=file_type, unused=unused, static=False))
                if line[:16] == "static const u8 ":
                    if line[16] == "*":
                        continue
                    text_title = line.split("[")[0][16:]
                    text_inside = line.split('"')[1]
                    # print(text_inside)
                    if len(line.split('//')) > 1:
                        unused = line.split("//")[1].lower().strip() == "unused" # if the string ends in // unused
                    else:
                        unused = False
                    static = True
                    to_translate_texts.append(BattleStringToTranslate(text_title=text_title, text_inside=text_inside, file_path=file_path, file_type=file_type, unused=unused, static=static))

                

    if not csv_file.exists():
        with csv_file.open('w', encoding='utf-8') as file:
            to_translate_texts[0].get_csv_init(file) # takes the first text out of the array and gets the original csv file according to the text class

    with csv_file.open("a", encoding='utf-8') as file:
        for to_translate_text in to_translate_texts:
            # file.write('"' + text_titles[i] + '","' + addresses[i] + '","' + text_insides[i] + '","' + str(file_path)+ '","' + file_type + '","' + unuseds[i] + '"\r')
            to_translate_text.write_csv(file)

if __name__ == '__main__':
    # DEBUG CODE
    # csv_file = Path("pythontools/results/contest_hall_debug_test.csv")
    # csv_file.unlink() # deletes "test_file.csv" to test if code works fresh
    # # document information
    # file_path = Path("data/scripts/contest_hall.inc")
    # scrape_file(file_path, csv_file, "inc_file")
    # print(list(Path("data/maps").glob("**/*/scripts.inc")))
    # print("\n")
    # print(list(Path("data/scripts").glob("**/*")))
    # exit()

    

    # # MAIN CODE

    # # inc files
    csv_file = Path("pythontools/results/inc_files.csv")
    # csv_file = Path("tools/scrape_strings_for_translation_python/results/event_ticket_2_debug.csv")
    csv_file.unlink() # deletes "test_file.csv" to test if code works fresh
    # folder information
    inc_files = list(Path("data/text").glob("**/*"))
    inc_files.extend(Path("data/maps").glob("**/*/scripts.inc"))
    inc_files.extend(Path("data/scripts").glob("**/*"))
    inc_files.append(Path("data/event_scripts.s"))
    for inc_file in inc_files:
        if inc_file == Path("data/text/braille.inc"):
            continue
        scrape_file(inc_file, csv_file, "inc_file")
        print(str(inc_file), 'scraped.')
    
    # # # u8 strings
    # # file_path = Path("src/strings.c")
    # # csv_file = Path("pythontools/results/strings_test.csv")
    # # csv_file.unlink()
    # # scrape_file(file_path, csv_file, "u8_string")
    # # print("src\strings.c scraped.")

    # # battle strings
    # file_paths = [Path("src/battle_message.c"), Path("src/map_name_popup.c"), Path("src/mevent_scripts.c"), Path("src/mystery_event_msg.c"), Path("src/text_input_strings.c")]
    # csv_file = Path("pythontools/results/battle_strings.csv")
    # csv_file.unlink()
    # for file_path in file_paths:
    #     scrape_file(file_path, csv_file, "battle_string")
    #     print(str(file_path),"scraped.")

