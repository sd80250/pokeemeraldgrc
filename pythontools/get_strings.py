import os
from pathlib import Path
from copy import copy, deepcopy

# folder information
inc_files = Path("data/text").glob("**/*")

# document information
file_path = Path("data/text/event_ticket_2.inc")
csv_file = Path("pythontools/results/test_file.csv")
# csv_file = Path("tools/scrape_strings_for_translation_python/results/event_ticket_2_debug.csv")
file_type = "inc_file" # what type of scraping should be done? i.e. how is the string formatted within the document?

class TextToTranslate:
    def __init__(self, text_title="", text_inside="", address="", file_path=None, file_type="", unused=False):
        self.text_title, self.text_inside, self.address, self.file_path, self.file_type, self.unused = text_title, text_inside, address, file_path, file_type, unused

    def append_text_inside(self, string):
        self.text_inside += string
    
    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, unused=self.unused)

    def write_csv(self, file):
        file.write('"' + self.text_title + '","' + self.address + '","' + self.text_inside + '","' + str(self.file_path)+ '","' + self.file_type + '","' + str(self.unused) +'"\r')

    def get_csv_init(self, file):
        file.write("text_title,address,text,file_name, file_type, unused\r")

class StringToTranslate(TextToTranslate):
    def __init__(self, text_title="", text_inside="", address="", file_path=None, file_type="", unused=False, aligned4=False):
        super().__init__(text_title, text_inside, address, file_path, file_type, unused)
        self.aligned4 = aligned4
    
    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, unused=self.unused, aligned4=self.aligned4)

    def write_csv(self, file):
        file.write('"' + self.text_title + '","' + self.address + '","' + self.text_inside + '","' + str(self.file_path)+ '","' + self.file_type + '","' + str(self.unused) +'","' + str(self.aligned4) + '"\r')
    
    def get_csv_init(self, file):
        file.write("text_title,address,text,file_name, file_type, unused, aligned4\r")


def scrape_file(file_path, csv_file, file_type):

    with file_path.open(encoding='utf-8') as file:
        # text for the whole file
        to_translate_texts = []
        isFirst = True

        # actual code         
        if file_type == "inc_file":
            next_is_unused = False # if the line says @ Unused, then the NEXT line will be the header of the unused line.
            while True:
                # print(text_titles, text_insides, addresses)
                line = file.readline()
                # print(line)
                # breaks if the line is None
                if not line:
                    to_translate_texts.append(copy(dialog_box))
                    break
                
                # if it doesn't start with a '\t' character, it's a new line or a new header
                if line == '\n': # i.e., the line is empty, except for the end.
                    pass
                elif line[0] == '\t':
                    # starts with '\t.string "'
                    if isFirst: # if there's anything that's written before the first text title and address, ignore it.
                        continue
                    dialog_box.append_text_inside(line[10:-2] + "\n") # this \n is not the 'official' line break found inside the actual game text itself
                elif line[0:4] == "    ":
                    # same as above, except indices have to be modified
                    if isFirst:
                        continue
                    dialog_box.append_text_inside(line[13:-2] +"\n")
                elif line[0] == '@':
                    # starts with '@', which starts all comments
                    if line[:8] == "@ Unused":
                        next_is_unused = True
                        print(next_is_unused)
                    continue
                else: # every file should start with this type of line
                    # gives us the text title and address
                    # this also means that a new line is being formed; this will be a surer way to tell when a new section is being formed
                    if isFirst:
                        isFirst = False
                    else:
                        to_translate_texts.append(copy(dialog_box))
                    text_title = line.split(":")[0] # gives the string until the first ':' character
                    address = ""
                    if len(line.split("@")) > 1:
                        address = line.split("@")[1].strip() # gives the string after the first "@" character.
                    dialog_box = TextToTranslate(text_title=text_title, text_inside="", address=address, file_path=file_path, file_type=file_type, unused=next_is_unused)
                    next_is_unused = False
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
                        print(line.split("//"))
                    else:
                        unused = False
                    aligned4 = True
                    to_translate_texts.append(StringToTranslate(text_title=text_title, text_inside=text_inside, file_path=file_path, file_type=file_type, unused=unused, aligned4=aligned4)) 
                

    if not csv_file.exists():
        with csv_file.open('w', encoding='utf-8') as file:
            if file_type == "inc_file":
                file.write("text_title,address,text,file_name, file_type,unused\r")
            if file_type == "u8_string":
                file.write("text_title,address,text,file_name, file_type,unused,aligned4\r")

    with csv_file.open("a", encoding='utf-8') as file:
        for to_translate_text in to_translate_texts:
            # file.write('"' + text_titles[i] + '","' + addresses[i] + '","' + text_insides[i] + '","' + str(file_path)+ '","' + file_type + '","' + unuseds[i] + '"\r')
            to_translate_text.write_csv(file)

if __name__ == '__main__':
    # # DEBUG CODE
    # csv_file.unlink() # deletes "test_file.csv" to test if code works fresh
    # scrape_file(file_path, csv_file, "inc_file")

    # MAIN CODE
    csv_file.unlink() # deletes "test_file.csv" to test if code works fresh
    for inc_file in inc_files:
        if inc_file == Path("data/text/braille.inc"):
            continue
        scrape_file(inc_file, csv_file, "inc_file")
        print(str(inc_file), 'scraped.')
    Path("pythontools/results/strings_test.csv").unlink()
    scrape_file(Path("src/strings.c"), Path("pythontools/results/strings_test.csv"), "u8_string")
    print("src\strings.c scraped.")

