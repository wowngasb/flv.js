# -*- coding: utf-8 -*-
import logging

from flvlib import tags
from flvlib import helpers
from flvlib.astypes import MalformedFLV

log = logging.getLogger('flvlib.debug-flv')
log.setLevel(logging.ERROR)

def debug_file(filename, quiet=False, metadata=False):
    try:
        f = open(filename, 'rb')
    except IOError, (errno, strerror):
        log.error("Failed to open `%s': %s", filename, strerror)
        return []

    flv = tags.FLV(f)

    if not quiet:
        print "=== `%s' ===" % filename

    ret_tags = []
    try:
        tag_generator = flv.iter_tags()
        for i, tag in enumerate(tag_generator):
            ret_tags.append(tag)
            if quiet:
                # If we're quiet, we just want to catch errors
                continue
            # Print the tag information
            print "#%05d %s" % (i + 1, tag)
            # Print the content of onMetaData tags
            if (isinstance(tag, tags.ScriptTag) and tag.name == "onMetaData"):
                helpers.pprint(tag.variable)
    except MalformedFLV, e:
        message = e[0] % e[1:]
        log.error("The file `%s' is not a valid FLV file: %s",
                  filename, message)
        return False
    except tags.EndOfFile:
        log.error("Unexpected end of file on file `%s'", filename)
        return False

    f.close()

    return ret_tags

def main():
    ret_tags = debug_file("source.flv", False, True)
    ret_tags

if __name__ == "__main__":
    main()
