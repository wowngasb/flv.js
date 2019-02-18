# -*- coding: utf-8 -*-
import logging

from flvlib import tags
from flvlib import helpers
from flvlib.astypes import MalformedFLV

log = logging.getLogger('flvlib.debug-flv')
log.setLevel(logging.ERROR)

def tryFixAudioTag(tag):
    return tag

def tryFixVideoTag(tag):
    return tag

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
    ret_msg = []
    try:
        tag_generator = flv.iter_tags()
        for i, tag in enumerate(tag_generator):
            # Print the tag information
            # Print the content of onMetaData tags
            msg = ''
            if (isinstance(tag, tags.ScriptTag) and tag.name == "onMetaData"):
                if not quiet:
                    helpers.pprint(tag.variable)
                    msg = "#%05d %s" % (i + 1, tag)
            elif isinstance(tag, tags.AudioTag) and tag.aac_packet_type == 1:  # AAC raw frame data
                msg = ("#%05d %s" % (i + 1, tag)).replace('AudioTag', 'AudioTag[%d]' % (len(tag.raw_data), ))
                tag = tryFixAudioTag(tag)
            elif isinstance(tag, tags.VideoTag) and tag.h264_packet_type == 1:  # AAC raw frame data
                msg = ("#%05d %s" % (i + 1, tag)).replace('VideoTag', 'VideoTag[%d]' % (tag.avc_raw.get('all_len', 0), ))
                tag = tryFixVideoTag(tag)
            else:
                if not quiet:
                    msg = "#%05d %s" % (i + 1, tag)

            ret_tags.append(tag)
            if msg:
                ret_msg.append(msg)
    except MalformedFLV, e:
        message = e[0] % e[1:]
        log.error("The file `%s' is not a valid FLV file: %s",
                  filename, message)
        return False
    except tags.EndOfFile:
        log.error("Unexpected end of file on file `%s'", filename)
        return False

    f.close()

    print "\n".join(ret_msg)
    return ret_tags

def main():
    ret_tags = debug_file("source.flv", False, True)
    ret_tags

if __name__ == "__main__":
    main()
