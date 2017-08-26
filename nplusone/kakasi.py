# -*- coding: utf-8 -*-
# Copyright: Damien Elmes <anki@ichi2.net>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
# Automatic reading generation with kakasi and mecab.
# See http://ichi2.net/anki/wiki/JapaneseSupport
#

import sys, os, platform, re, subprocess
from utils import mungeForPlatform, escapeText, getStartupInfo, isWin

kakasiArgs = ["-isjis", "-osjis", "-u", "-JH", "-KH"]

class Kakasi(object):

    def __init__(self, kakasiArgs=kakasiArgs):
        self.kakasi = None
        self.kakasiArgs = kakasiArgs

    def setup(self):
        base = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'support') + '/'
        self.kakasiCmd = mungeForPlatform(
            [base + "kakasi"] + self.kakasiArgs)
        os.environ['ITAIJIDICT'] = base + "itaijidict"
        os.environ['KANWADICT'] = base + "kanwadict"
        if not isWin:
            os.chmod(self.kakasiCmd[0], 0o755)

    def ensureOpen(self):
        if not self.kakasi:
            self.setup()
            try:
                self.kakasi = subprocess.Popen(
                    self.kakasiCmd, bufsize=-1, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    startupinfo=getStartupInfo())
            except OSError:
                raise Exception("Please install kakasi")

    def reading(self, expr):
        self.ensureOpen()
        expr = escapeText(expr)
        self.kakasi.stdin.write(expr.encode("sjis", "ignore") + b'\n')
        self.kakasi.stdin.flush()
        res = self.kakasi.stdout.readline().rstrip(b'\r\n').decode("sjis")
        return res

