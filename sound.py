import sys

if False:#sys.platform == 'darwin':
    from AppKit import NSSound
    class Sound(object):
        def __init__(self, path):
            self.sound = NSSound.alloc()
            self.sound.initWithContentsOfFile_byReference_(path, True)
        def play(self):
            self.sound.play()
        def stop(self):
            self.sound.stop()
        @property
        def playing(self):
            return self.sound.isPlaying()
elif sys.platform == 'win32':
    from win32com.client import Dispatch
    class Sound(object):
        def __init__(self, path):
            self.mp = Dispatch('WMPlayer.OCX')
            self.sound = self.mp.newMedia(path)
            self.mp.currentPlaylist.appendItem(self.sound)
        def play(self):
            self.mp.controls.play()
        def stop(self):
            self.mp.controls.stop()
        @property
        def playing(self):
            return self.mp.playState == 9
else:
    class Sound(object):
        def __init__(self, path):
            pass
        def play(self):
            pass
        def stop(self):
            pass
        @property
        def playing(self):
            return False
            