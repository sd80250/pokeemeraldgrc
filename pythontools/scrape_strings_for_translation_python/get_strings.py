import os
from pathlib import Path
from copy import copy, deepcopy

# folder information
inc_files = Path("data/text").glob("**/*")

# document information
file_path = Path("data/text/event_ticket_2.inc")
csv_file = Path("tools/scrape_strings_for_translation_python/results/test_file.csv")
# csv_file = Path("tools/scrape_strings_for_translation_python/results/event_ticket_2_debug.csv")
file_type = "inc_file" # what type of scraping should be done? i.e. how is the string formatted within the document?

class TextToTranslate:
    def __init__(self, text_title="", text_inside="", address="", unused = False): # TODO: contest_strings.inc has a few mass unused segments to manually add
        self.text_title, self.text_inside, self.address, self.unused = text_title, text_inside, address, unused

    def append_text_inside(self, string):
        self.text_inside += string
    
    def __copy__(self):
        return type(self)(text_title=self.text_title, text_inside=self.text_inside,address=self.address, unused=self.unused)


def scrape_file(file_path, csv_file, file_type):

    with file_path.open(encoding='utf-8') as file:
        # text for the whole file
        dialog_boxes = []
        isFirst = True

        # actual code         
        if file_type == "inc_file":
            while True:
                # print(text_titles, text_insides, addresses)
                line = file.readline()
                # print(line)
                # breaks if the line is None
                if not line:
                    dialog_boxes.append(copy(dialog_box))
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
                        dialog_box.unused = True
                    continue
                else: # every file should start with this type of line
                    # gives us the text title and address
                    # this also means that a new line is being formed; this will be a surer way to tell when a new section is being formed
                    if isFirst:
                        isFirst = False
                    else:
                        dialog_boxes.append(copy(dialog_box))
                    text_title = line.split(":")[0] # gives the string until the first ':' character
                    address = ""
                    if len(line.split("@")) > 1:
                        address = line.split("@")[1].strip() # gives the string after the first "@" character.
                    dialog_box = TextToTranslate(text_title=text_title, text_inside="", address=address)
                    # for the first name and address line, you don't want the system to record the text (there is no text yet)        
        if file_type == "u8_string":
            pass

    if not csv_file.exists():
        with csv_file.open('w', encoding='utf-8') as file:
            file.write("text_title,address,text,file_name, file_type, unused\r")

    with csv_file.open("a", encoding='utf-8') as file:
        for dialog_box in dialog_boxes:
            # file.write('"' + text_titles[i] + '","' + addresses[i] + '","' + text_insides[i] + '","' + str(file_path)+ '","' + file_type + '","' + unuseds[i] + '"\r')
            file.write('"' + dialog_box.text_title + '","' + dialog_box.address + '","' + dialog_box.text_inside + '","' + str(file_path)+ '","' + file_type + '","' + dialog_box.unused +'"\r')

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

