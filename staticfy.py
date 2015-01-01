"""
fix_file will add
{% load staticfiles %} to the top line
and enclose any href or src attributes inside
{% static ... %}
There is currently no catching mechanism for relative paths (ie:  ../Dir/file.txt )
"""
def fix_file(filename):     # give it the name of the file
    f = open(filename, 'r')      # open the file in read only mode
    file_contents = f.read()     # make a string full of the contents
    f.close()                    # close the readable file

    # TODO: if the string is empty, bail out ( or just don't pass it empty files ;) )

    # TODO make a backup copy of the contents in case shit happens (priority)

    new_contents = "{% load staticfiles %}\n" + file_contents
    file_contents = new_contents

    src_found = 0               # holds index of current change or -1 for EOF
    href_found = 0              # holds index of current change or -1 for EOF
    done = 0                    # holds -1 when both src and href checks reach EOF
    while done != -1:           # while not EOF look for any instance of 'src=' or 'href='
        while src_found != -1:                                      # if prev search didn't reach EOF
            src_found = file_contents.find("src=", src_found)       # find an instance of src
            if src_found != -1:                                     # if current search didn't reach EOF
                src_found += 4                                      # position after =
            else:
                break
            new_contents = file_contents[:src_found] + '\"{% static ' + file_contents[src_found:]  # append "{% static
            file_contents = new_contents                            # retain new contents
            quotes = file_contents.find("\"", (src_found + 13))     # find the next available "
            quotes += 1                                             # move to next spot for append
            new_contents = file_contents[:quotes] + ' %}\"' + file_contents[quotes:]  # append ' %}"'
            file_contents = new_contents                            # write to new string
        while href_found != -1:                                     # if prev search didn't reach EOF
            href_found = file_contents.find("href=", href_found)    # find an instance of href
            if href_found != -1:                                    # if current search didn't reach EOF
                href_found += 5                                     # position after =
            else:
                break
            new_contents = file_contents[:href_found] + '\"{% static ' + file_contents[href_found:]  # append "{% static
            file_contents = new_contents                            # retain new contents
            quotes = file_contents.find("\"", (href_found + 13))    # find the next available whitespace
            quotes += 1                                             # move to next spot for append
            new_contents = file_contents[:quotes] + ' %}\"' + file_contents[quotes:]  # append ' %}'
            file_contents = new_contents                            # write to new string
        if href_found == -1 and src_found == -1:                    # if both reach EOF kill loop
            done = -1

    # when process is complete
    f = open(filename, 'w')    # open the original file in write mode
    f.write(file_contents)     # overwrite it
    f.close()                  # save it