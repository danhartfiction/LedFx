from ledfx.effects.audio import AudioReactiveEffect, FREQUENCY_RANGES
from ledfx.effects.colorrainbow import ColorRainbowEffect 
import voluptuous as vol
import numpy as np
import time
import statistics
import requests
import threading

class DranoBeatAudioEffect(AudioReactiveEffect, ColorRainbowEffect):

    NAME = "DranoBeat"
    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('frequency_range', description='Frequency range for the beat detection', default = 'bass'): vol.In(list(FREQUENCY_RANGES.keys())),
    })

    def config_updated(self, config):
        self._frequency_range = np.linspace(
            FREQUENCY_RANGES[self.config['frequency_range']].min,
            FREQUENCY_RANGES[self.config['frequency_range']].max,
            20)

    def updateThread(self):
        self.getBeat()
        if not hasattr(self, 'beatThreadStart'):
            print("afa")
            self.beatThreadStart = True
            threading.Timer(self.next_beat - time.time(), self.beatThread).start()
            self.i = 0
        threading.Timer(2, self.updateThread).start()

    def beatThread(self):
        self.i += 1
        print("BEAT {}!".format(self.i))
        self.pixels = self.apply_rainbow(True)
        now = time.time()
        if self.next_beat - 60/self.bpm < now:
            self.next_beat += 60/self.bpm
        print("next in {}".format(self.next_beat - now))
        threading.Timer(self.next_beat - now, self.beatThread).start()
        self.faderThreadStart = True
        threading.Timer(.1, self.fader).start()
      
    def fader(self):
#        print("fading")
        self.pixels = np.zeros(shape=(self.pixel_count, 3))

    def getBeat(self):
        r = requests.get("http://127.0.0.1:5000/")
        data = r.text.split(':')
        self.next_beat = float(data[0])
        self.bpm = float(data[1])
#        self.next_beat = time.time() + 1
#        self.bpm = 60

    def audio_data_updated(self, data):
        if not hasattr(self, 'colormap'):
            self.colormap = np.zeros(shape=(self.pixel_count, 3)) 
            self.updateThread()
