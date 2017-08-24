import sys
import re
import subprocess
import os

def mungeForPlatform(popen):
    if sys.platform == "win32":
        popen = [os.path.normpath(x) for x in popen]
        popen[0] += ".exe"
    elif sys.platform == "darwin":
        popen[0] += ".lin"
    return popen


def escapeText(text):
    # strip characters that trip up kakasi/mecab
    text = text.replace("\n", " ")
    text = text.replace(u'\uff5e', "~")
    # removed strip html
    text = re.sub("<br( /)?>", "---newline---", text)
    text = text.replace("---newline---", "<br>")
    return text


def getStartupInfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        try:
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        except:
            si.dwFlags |= subprocess._subprocess.STARTF_USESHOWWINDOW
    else:
        si = None

    return si

def utf8String(string):
    return unicode(string, 'utf-8')