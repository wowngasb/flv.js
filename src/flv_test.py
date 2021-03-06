# -*- coding: utf-8 -*-
import logging
import urllib2
import os
from flvlib import tags
from flvlib import helpers
from flvlib.astypes import MalformedFLV

log = logging.getLogger('flvlib.debug-flv')
log.setLevel(logging.ERROR)

def tryFixAudioTag(tag):
    return tag

def tryFixVideoTag(tag):
    return tag

class HttpFile(object):
    def __init__(self, f, block = 8096):
        self.f = f
        self.block = block

        self._i = 0
        _size = self.f.headers.get('content-length', '-1')
        self._size = int(_size) if _size.isalnum() and int(_size) >= 0 else -1
        self._buffer = self.f.read(self.block)
        self._eof = False
        self._n = 0

    def read(self, n = 8096):
        n = int(n) if n and int(n) > 0 else 0
        if n <= 0 or self._i >= len(self._buffer):
            return ''

        _i = self._i
        self._i += n
        while self._i > len(self._buffer) and not self._eof:
            tmp = self.f.read(self.block)
            if not tmp or len(tmp) < self.block:
                self._eof= True

            self._buffer += tmp if tmp else ''

        self._n += 1
        if self._n % 10 == 0:
            pass
        else:
            print "read %d:%d\n" % (_i, n)
        return self._buffer[_i:self._i]

    def seek(self, i, b = os.SEEK_SET):
        i = int(i) if i and int(i) > 0 else 0

        if b == os.SEEK_CUR:
            self._i += i
        elif b == os.SEEK_SET:
            self._i = i
        elif b == os.SEEK_END:
            raise NotImplementedError("no end")

    def tell(self):
        return self._i

def debug_file(filename, quiet=False, metadata=False):
    try:
        if filename.startswith('http://') or filename.startswith('https://'):
            f = HttpFile(urllib2.urlopen(filename))
        else:
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
    globals()['STRICT_PARSING'] = False
    ret_tags = debug_file("http://s4-play.xdysoft.com/xdylive/ud1nPGQ0.flv", False, False)
    ret_tags

if __name__ == "__main__":
    main()
