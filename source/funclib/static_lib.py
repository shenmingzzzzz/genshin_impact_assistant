from source.util import *

global W_KEYDOWN, cvAutoTrackerLoop
W_KEYDOWN = False
cvAutoTrackerLoop = None

if config_json["capture_mode"] == "compatibility":
    d3d_capture = None
else:
    d3d_capture = None
def get_handle():
    if not config_json["cloud_genshin"]:
        handle = ctypes.windll.user32.FindWindowW(None, 'Genshin Impact')
        if handle != 0:
            return handle
        handle = ctypes.windll.user32.FindWindowW(None, '原神')
        if handle != 0:
            return handle
        
    else:
        handle = ctypes.windll.user32.FindWindowW("Qt5152QWindowIcon", '云·原神')
        if handle != 0:
            return 331454

HANDLE = get_handle()


if __name__ == '__main__':
    pass
