import sys
import os

path = '/home/kullanici_adiniz/YZDBHTKS'
if path not in sys.path:
    sys.path.append(path)

os.chdir(path)

from dashboard import app as application