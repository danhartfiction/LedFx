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
            if tick_avg < .1:
                self.empty_ticks += 1
                if self.empty_ticks > 150: # End of song
                    print("End of song.")
                    self.tick_samples = []
                    self.samples= []
                    self.bmp_list = []
                    self.sampleStartTime = now
                    self.beat = False
            elif tick_avg > culmative_avg * 1.1:
                if now - self.prev_beat > 60/self.maxBPM:
                    bpm = int(60 / (now - self.prev_beat))
                    if len(self.bpm_list) < 4:
                        if bpm > 40:
                            self.bpm_list.append(bpm)
                            self.bpm_avg = round(statistics.mean(self.bpm_list))
                            self.beat = True
                    else:
                        self.bpm_avg = round(statistics.mean(self.bpm_list))
                        if abs(self.bpm_avg - bpm) < 35:
                            self.bpm_list.append(bpm)
                            self.bpm_avg = round(statistics.mean(self.bpm_list))
#                    print("average bpm: {}".format(self.bpm_avg))
            if now - self.next_beat > 0:
                temp_next_beat = self.next_beat
                self.next_beat = self.next_beat + 60/self.bpm_avg
                self.prev_beat = temp_next_beat
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
            self.empty_ticks = 0
            self.maxBPM = 180
            self.bpm_avg = 60
            self.samples = []
            self.tick_samples = []
            self.bpm_list = []
            self.colormap = np.zeros(shape=(self.pixel_count, 3))
            self.tick_size = 60 / (self.maxBPM*10)
            self.tick_start = self.sampleStartTime
            self.prev_beat = now
            self.next_beat = now
            self.beat = False

        # Grab the filtered and interpolated melbank data
        magnitude = np.max(data.sample_melbank(list(self._frequency_range)))

        self.pixels = self.apply_rainbow(abs(now - self.next_beat))
        self.updateBeat(magnitude, now)
