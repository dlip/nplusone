# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
# See http://ichi2.net/anki/wiki/JapaneseSupport
#

import sys, os, platform, re, subprocess
from utils import mungeForPlatform, escapeText, getStartupInfo
from kakasi import Kakasi

mecabArgs = []

class Mecab(object):

    def __init__(self, mecabArgs=mecabArgs):
        self.mecab = None
        self.mecabArgs = mecabArgs
        self.kakasi = Kakasi()

    def setup(self):
        base = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'support') + '/'
        self.mecabCmd = mungeForPlatform(
            [base + "mecab"] + self.mecabArgs + [
                '-d', base, '-r', base + "mecabrc"])
        os.environ['DYLD_LIBRARY_PATH'] = base
        os.environ['LD_LIBRARY_PATH'] = base
        if not sys.platform == "win32":
            os.chmod(self.mecabCmd[0], 0o755)

    def ensureOpen(self):
        if not self.mecab:
            self.setup()
            try:
                self.mecab = subprocess.Popen(
                    self.mecabCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=getStartupInfo())
            except OSError:
                raise Exception("Please ensure your Linux system has 64 bit binary support.")

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.mecab.stdin.write(expr.encode("utf-8", "ignore") + b'\n')
        self.mecab.stdin.flush()
        expr = self.mecab.stdout.readline().rstrip(b'\r\n').decode('utf-8')

        out = []
        for node in expr.split("\t"):
            if not node:
                break
            token = {}
            (kanji, reading, dict_form, dict_form_reading) = re.match("(.+)\[(.*)\]\[(.*)\]\[(.*)\]", node).groups()
            # not kanji or lacking a reading
            if not reading or not re.match(u'.*[\u4e00-\u9faf]+.*', kanji):
                token['surface'] = kanji
                out.append(token)
                continue

            reading = self.kakasi.reading(reading)
            dict_form_reading = self.kakasi.reading(dict_form_reading)

            # Readings using katakana ー dont convert to hiragana so try to take from dict form reading
            surface = self.anki_reading(kanji, reading)
            inside_brackets_match = re.match(u'.*\[(.*[ー].*)\].*', surface)
            if inside_brackets_match:
                inside_brackets = inside_brackets_match.group(1)
                surface_reading = dict_form_reading[0:len(inside_brackets)]
                surface = re.sub(u'(\[.*\])', '[' + dict_form_reading[0:len(surface_reading)] + ']', surface)

            after_brackets_match = re.match(u'.*\](.*[ー]+)', surface)
            if after_brackets_match:
                after_brackets = after_brackets_match.group(1)
                surface_suffix = kanji[-len(after_brackets):]
                surface = re.sub(u'\].*', ']' + surface_suffix, surface)

            token['surface'] = surface
            token['dict_form'] = dict_form
            token['dict_form_reading'] = self.anki_reading(dict_form, dict_form_reading).strip()

            out.append(token)
        return out

    def anki_reading(self, kanji, reading):
        # strip matching characters and beginning and end of reading and kanji
        # reading should always be at least as long as the kanji
        placeL = 0
        placeR = 0
        # if its not all kanji until the end, step from right to left to find reading
        # This is to handle when we have 'ー' but its a kanji only
        if not re.match(u'[\u4e00-\u9faf]+$', kanji):
            for i in range(1,len(kanji)):
                if kanji[-i] != reading[-i] and reading[-i] != u'ー':
                    break
                placeR = i
        for i in range(0,len(kanji)-1):
            if kanji[i] != reading[i]:
                break
            placeL = i+1
        if placeL == 0:
            if placeR == 0:
                return " %s[%s]" % (kanji, reading)
            else:
                return " %s[%s]%s" % (
                    kanji[:-placeR], reading[:-placeR], reading[-placeR:])
        else:
            if placeR == 0:
                return "%s %s[%s]" % (
                    reading[:placeL], kanji[placeL:], reading[placeL:])
            else:
                return "%s %s[%s]%s" % (
                    reading[:placeL], kanji[placeL:-placeR],
                    reading[placeL:-placeR], reading[-placeR:])