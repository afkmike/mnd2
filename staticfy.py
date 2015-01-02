"""
fix_file will add
{% load staticfiles %} to the top line
and enclose any href or src attributes inside
{% static ... %}
There is currently no catching mechanism for relative paths (ie:  ../Dir/file.txt )
"""
import sys, os


def fix_file(filename):     # give it the name of the file -- Takes a List
    delete_list = [] # for files that can be deleted
    for files in filename:
        f = open(files, 'r')      # open the file in read only mode
        file_contents = f.read()     # make a string full of the contents
        f.close()                    # close the readable file

        # TODO: if the string is empty, bail out ( or just don't pass it empty files ;) )



        copy_filename = "copyOf"+files
        f = open(copy_filename,'w')
        f.write(file_contents)
        f.close()

        new_contents = "{% load staticfiles %}\n" + file_contents
        file_contents = new_contents

        src_found = 0               # holds index of current change or -1 for EOF
        href_found = 0              # holds index of current change or -1 for EOF
        done = 0                    # holds -1 when both src and href checks reach EOF
        LINK_OPEN = '\"{% static '
        LINK_CLOSE = ' %}\"'
        STATIC_LEN_OPEN = len(LINK_OPEN)+1
        SRC_OFFSET = 4
        HREF_OFFSET = 5
        try:
            while done != -1:           # while not EOF look for any instance of 'src=' or 'href='
                while src_found != -1:                                      # if prev search didn't reach EOF
                    src_found = file_contents.find("src=", src_found)       # find an instance of src
                    if src_found != -1:                                     # if current search didn't reach EOF
                        src_found += SRC_OFFSET                             # position after =
                    else:
                        break
                    new_contents = file_contents[:src_found] + LINK_OPEN + file_contents[src_found:]  # append "{% static
                    file_contents = new_contents                            # retain new contents
                    quotes = file_contents.find("\"", (src_found + STATIC_LEN_OPEN))     # find the next available "
                    quotes += 1                                             # move to next spot for append
                    new_contents = file_contents[:quotes] + LINK_CLOSE + file_contents[quotes:]  # append ' %}"'
                    file_contents = new_contents                            # write to new string
                while href_found != -1:                                     # if prev search didn't reach EOF
                    href_found = file_contents.find("href=", href_found)    # find an instance of href
                    if href_found != -1:                                    # if current search didn't reach EOF
                        href_found += HREF_OFFSET                           # position after =
                    else:
                        break
                    new_contents = file_contents[:href_found] + LINK_OPEN + file_contents[href_found:]  # append "{% static
                    file_contents = new_contents                            # retain new contents
                    quotes = file_contents.find("\"", (href_found + STATIC_LEN_OPEN))    # find the next available whitespace
                    quotes += 1                                             # move to next spot for append
                    new_contents = file_contents[:quotes] + LINK_CLOSE + file_contents[quotes:]  # append ' %}'
                    file_contents = new_contents                            # write to new string
                if href_found == -1 and src_found == -1:                    # if both reach EOF kill loop
                    done = -1

            # when process is complete
            f = open(files, 'w')    # open the original file in write mode
            f.write(file_contents)     # overwrite it
            f.close()                  # save it
            delete_list.append(copy_filename)
        except:
            c = open(copy_filename,'r')
            contents = c.read()
            f = open(files, 'w')
            f.write(contents)
            f.close()
            c.close()

    return delete_list


if __name__ == "__main__":
    files = [                      # Add files to manage here

    ]
    delete_list = []
    if files: # Make sure files is not empty
        delete_list = fix_file(files)