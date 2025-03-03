import sys
path = '/home/Black4545/netwatch'
if path not in sys.path:
    sys.path.append(path)

from run import app as application 