"""
STATICFY is a django integration script for new html files
Owned by afkconcepts
author : mike
"""
import sys, os, log_manager

log = log_manager.log_manager("Log.txt")

def get_contents(filename):
    """######################################################################################
    # places target file into a string object and calls make_backup prior to any other      #
    # method gaining access to the string or original file                                  #
    # ###USAGE: this function can be "independently" called by process() or any flow control#
    ######################################################################################"""
    f = open(filename, 'r')
    contents = f.read()
    f.close()
    make_backup(contents, filename)
    return contents

def make_backup(contents, name):
    """######################################################################################
    # makes a carbon copy of the original file before modifications                         #
    # ###USAGE: this function is called by get_contents to ensure backup is done prior to   #
    #           any other method accessing data                                             #
    ######################################################################################"""
    copy_filename = "copyOf" + name
    make_new_file(contents, copy_filename)
    log.log.info("Made backup copy of " + name + " named " + copy_filename)
        # TODO throw if backup fails

def extend_base(contents):
    """######################################################################################
    # check for {% extends "base.html" %} tag then inserts after doctype                    #
    # ###USAGE: this function can be "independently" called by process or any flow control  #
    #           HOWEVER it will be called by default_blocks() to ensure inheritance applies #
    #           to the given file                                                           #
    ######################################################################################"""
    EXTENDS_BASE_TAG = '{% extends \"base.html\" %}'
    EXTENDS_BASE_INDEX = contents.find(EXTENDS_BASE_TAG)
    if EXTENDS_BASE_INDEX > 0:
        log.log.info("Extends tag found prior to insert. Process aborted.")
        return contents
    else:
        log.log.info("Extends base.html tag was inserted")
        AFTER_DOCTYPE = contents.find(">")+1  # safe enchant to +3   o.0
        new_contents = contents[:AFTER_DOCTYPE] + "\n" + EXTENDS_BASE_TAG + "\n" + contents[AFTER_DOCTYPE:]
        return new_contents

def load_staticfiles(contents):
    """######################################################################################
    # check for {% load staticfiles %} tag                                                  #
    # then inserts after either {% extends base.html %} (if it exists) or doctype           #
    # ###USAGE: this function will be called by staticfy_resource() to ensure staticfiles   #
    #           is loaded before any linking is attempted                                   #
    ######################################################################################"""
    LOAD_SF_TAG = "{% load staticfiles %}"
    LOAD_SF_INDEX = contents.find(LOAD_SF_TAG)
    if LOAD_SF_INDEX > 0:
        print "LOAD STATICFILES TAG EXISTS"
        return contents
    else:
        EXTENDS_BASE_TAG = "{% extends \"base.html\" %}"
        EXTENDS_BASE_INDEX = contents.find(EXTENDS_BASE_TAG)
        if EXTENDS_BASE_INDEX > 0:
            log.log.info("Load staticfiles tag inserted after extends base.html tag")
            EXTENDS_BASE_INDEX += len(EXTENDS_BASE_TAG)+1
            new_contents = contents[:EXTENDS_BASE_INDEX] + "\n" + LOAD_SF_TAG + "\n" + contents[EXTENDS_BASE_INDEX:]
        else:
            log.log.info("Load staticfiles tag inserted after DOCTYPE tag")
            AFTER_DOCTYPE = contents.find(">")+1
            new_contents = contents[:AFTER_DOCTYPE] + "\n" + LOAD_SF_TAG + "\n" + contents[AFTER_DOCTYPE:]
        return new_contents

def staticfy_resource(contents, res_type):
    """######################################################################################
    #  designed to link all resources to the staticfiles dir                                #
    #  calls load_staticfiles() to ensure the files are loaded before trying to link        #
    #  generalized to require you pass the resource type (ie. src=, href= (REMEMBER = !))   #
    # ###USAGE: Don't forget the = or it won't work right!                                  #
    ######################################################################################"""
    # TODO There is currently no catching mechanism for relative paths (ie:  ../Dir/file.txt )
    contents = load_staticfiles(contents)

    RES_INDEX = 0
    STATIC_TAG_FRONT = '\"{% static '
    STATIC_TAG_BACK = ' %}\"'
    STATIC_FRONT_LEN = len(STATIC_TAG_FRONT)+1
    STATIC_BACK_LEN = len(STATIC_TAG_BACK)+1
    OFFSET = len(res_type)
    while RES_INDEX != -1:
        RES_INDEX = contents.find(res_type, RES_INDEX)
        if RES_INDEX != -1:
            RES_INDEX += OFFSET
        else:
            break
        ALREADY_LINKED = contents.find(STATIC_TAG_FRONT, RES_INDEX)
        if ALREADY_LINKED == -1:
            log.log.info("Resource of type: " + res_type + " FOUND! STATICFYING!")
            new_contents = contents[:RES_INDEX] + STATIC_TAG_FRONT + contents[RES_INDEX:]
            contents = new_contents
            quotes = contents.find("\"", (RES_INDEX+STATIC_FRONT_LEN))
            quotes += 1
            new_contents = contents[:quotes] + STATIC_TAG_BACK + contents[quotes:]
            contents = new_contents
        else:
            break
    log.log.info("ALL RESOURCES ARE STATICFIED!")
    return contents

def url_conf(contents):
    """######################################################################################
    # designed to match all hyperlinks to their django url configuration                    #
    # ###USAGE: this function can be "independently" called by process() or any flow control#
    ######################################################################################"""
    # TODO There is currently no catching mechanism for relative paths (ie:  ../Dir/file.txt )
    link_index = 0
    bracket_index = 0
    ANCHOR_TAG = '<a'
    ATTRIBUTE = 'href='
    OFFSET_1 = len('href="{% ')             # pos to add 'url'
    OFFSET_2 = len('href="{% static "')     # pos to put trimmed url
    while link_index != -1:
        link_index = contents.find(ANCHOR_TAG, bracket_index)
        if link_index == -1:
            break
        else:
            ATTRIBUTE_INDEX = contents.find(ATTRIBUTE, link_index)
            DOT_INDEX = contents.find('.', (ATTRIBUTE_INDEX + OFFSET_2))
            bracket_index = contents.find('}', DOT_INDEX)
            URL_FRONT = ATTRIBUTE_INDEX + OFFSET_2
            URL = contents[URL_FRONT: DOT_INDEX]
            log.log.info("Url revised : " + URL)
            NEW_LINK = 'url \"' + URL + '\" %'
            new_contents = contents[:(ATTRIBUTE_INDEX+OFFSET_1)] + NEW_LINK + contents[bracket_index:]
            contents = new_contents
    return contents

def default_blocks(contents):
    """######################################################################################
    #  designed to insert the default inherited blocks (head_block and body_content)        #
    #  declarations are verbose to avoid naming errors                                      #
    #  could probably automate to make less redundant, but must remain scalable             #
    # ###USAGE: Don't call twice until catches are added!                                   #
    ######################################################################################"""
    contents = extend_base(contents)

    HEAD_BLOCK_OPEN = '{% block head_block %}'
    BODY_BLOCK_OPEN = '{% block body_content %}'
    BLOCK_CLOSE = '{% endblock %}'

    HEAD_TAG = '<head>'
    HEAD_FRONT = contents.find(HEAD_TAG)
    if HEAD_FRONT > -1:
        HEAD_BACK = HEAD_FRONT + len(HEAD_TAG)
        new_contents = contents[:HEAD_FRONT] + HEAD_BLOCK_OPEN + contents[HEAD_BACK:]
        contents = new_contents
        log.log.info("Head block inserted")

    HEAD_CLOSE_TAG = '</head>'
    HEAD_CLOSE_FRONT = contents.find(HEAD_CLOSE_TAG)
    if HEAD_CLOSE_FRONT > -1:
        HEAD_CLOSE_BACK = HEAD_CLOSE_FRONT + len(HEAD_CLOSE_TAG)
        new_contents = contents[:HEAD_CLOSE_FRONT] + BLOCK_CLOSE + contents[HEAD_CLOSE_BACK:]
        contents = new_contents
        log.log.info("Head block close inserted")

    BODY_TAG = '<body>'
    BODY_FRONT = contents.find(BODY_TAG)
    if BODY_FRONT > -1:
        BODY_BACK = BODY_FRONT + len(BODY_TAG)
        new_contents = contents[:BODY_FRONT] + BODY_BLOCK_OPEN + contents[BODY_BACK:]
        contents = new_contents
        log.log.info("Body block inserted")

    BODY_CLOSE_TAG = '</body>'
    BODY_CLOSE_FRONT = contents.find(BODY_CLOSE_TAG)
    if BODY_CLOSE_FRONT > -1:
        BODY_CLOSE_BACK = BODY_CLOSE_FRONT + len(BODY_CLOSE_TAG)
        new_contents = contents[:BODY_CLOSE_FRONT] + BLOCK_CLOSE + contents[BODY_CLOSE_BACK:]
        contents = new_contents
        log.log.info("Body block close inserted")

    return contents

def make_new_file(contents, name):
    """###############################################
    # general utility for creating a new file        #
    # ###USAGE: use anywhere                         #
    ###############################################"""
    f = open(name, 'w')     # create/open the file in write mode
    f.write(contents)       # write/overwrite it
    f.close()               # save it
    log.log.info("File saved: " + name)

def process(a_file, mode):
    """######################################################################################
    # single call helper function encapsulates flow control by file type                    #
    # ###USAGE: this function is called from __main__ to automate typical processing        #
    ######################################################################################"""
    # TODO implement base template configurations!!
    # (MODE == PAGE_TYPE)
    # if mode = base

    # if mode = content
    # Standard Child template process:
    if mode == 1:
        contents = get_contents(a_file)
        contents = default_blocks(contents)
        contents = staticfy_resource(contents, "src=")
        contents = staticfy_resource(contents, "href=")
        contents = url_conf(contents)
        make_new_file(contents, a_file)
    return

if __name__ == "__main__":
    if len(sys.argv) < 1:               # check for command line args first
        files = [                       # Or Add files to manage here
            # "example.html", "another.htm"
        ]
        mode = 1
    else:
        files = sys.argv
        mode = 1

    for each_file in files:
        process(each_file, mode)