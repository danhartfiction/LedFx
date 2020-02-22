from ledfx.effects.audio import AudioReactiveEffect, FREQUENCY_RANGES
from ledfx.effects.colorrainbow import ColorRainbowEffect 
import voluptuous as vol
import numpy as np
import time
import statistics

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

    def updateBeat(self, y, now):
        self.tick_samples.append(y)
        if now - self.tick_start > self.tick_size:
            tick_avg = statistics.mean(self.tick_samples)
            self.samples.append(tick_avg)
            culmative_avg = statistics.mean(self.samples)
            if (tick_avg > .1 and tick_avg > culmative_avg * 1.5):
                if now - self.prev_beat > 60/self.maxBPM:
                    print('beat')
                    bpm = int(60 / (now - self.prev_beat))
                    bpm_avg = 60
                    if len(self.bpm_list) < 4:
                        if bpm > 40:
                            print("Found bpm: {}".format(bpm))
                            self.bpm_list.append(bpm)
                            bpm_avg = statistics.mean(self.bpm_list)
                    else:
                        bpm_avg = statistics.mean(self.bpm_list)
                        if abs(bpm_avg - bpm) < 35:
                            print("appending bpm: {}".format(bpm))
                            self.bpm_list.append(bpm)
                    self.prev_beat = now
                    self.next_beat = now + 60/bpm_avg
                    print("average bpm: {}".format(bpm_avg))
                    self.beat = True
            if len(self.samples) > 50:
                self.samples = self.samples[25:]
            if len(self.bpm_list) > 24:
                self.bpm_list = self.bpm_list[8:]
            self.tick_samples = []
            self.tick_start = now

    def audio_data_updated(self, data):
        now = time.time()
        if not hasattr(self, 'beat'):
            print("INIT!")
            self.sampleStartTime = now
            self.maxBPM = 180
            self.samples = []
            self.tick_samples = []
            self.bpm_list = []
            self.colormap = np.zeros(shape=(self.pixel_count, 3))
            self.tick_size = 60 / (self.maxBPM*10)
            self.tick_start = self.sampleStartTime
            self.prev_beat = self.sampleStartTime
            self.next_beat = now - 1000
            self.beat = False

        # Grab the filtered and interpolated melbank data
        magnitude = np.max(data.sample_melbank(list(self._frequency_range)))

        self.updateBeat(magnitude, now)
        self.pixels = self.apply_rainbow(abs(now - self.next_beat))
