import sys

if sys.platform == 'darwin':
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
            