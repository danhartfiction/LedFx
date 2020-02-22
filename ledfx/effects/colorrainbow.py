from ledfx.effects.temporal import TemporalEffect
from ledfx.effects.modulate import ModulateEffect
from ledfx.color import COLORS, GRADIENTS
from ledfx.effects import Effect
import voluptuous as vol
import numpy as np
import logging

_LOGGER = logging.getLogger(__name__)

@Effect.no_registration
class ColorRainbowEffect(Effect):

    CONFIG_SCHEMA = vol.Schema({
        vol.Optional('gradient_name', description='Preset gradient name', default = 'Spectral'): vol.In(list(GRADIENTS.keys())),
        vol.Optional('gradient_roll', description='Amount to shift the gradient', default = 0): vol.Coerce(int),
        vol.Optional('gradient_method', description='Function used to generate gradient', default = 'cubic_ease'): vol.In(["cubic_ease", "bezier"]),
    })

    def apply_rainbow(self, dt):
        output = np.zeros(shape=(self.pixel_count, 3))
        if dt < .1:
            print("beat")
            rainbow = []
            rainbow.append([255, 0, 0])
            rainbow.append([255, 165, 0])
            rainbow.append([255, 255, 0])
            rainbow.append([0, 128, 0])
            rainbow.append([0, 0, 255])
            rainbow.append([75, 00, 130])
            rainbow.append([238, 130, 238])
            pixels_per_color = int(self.pixel_count / len(rainbow))
            for i in range(self.pixel_count):
                index = int(i / pixels_per_color)
                if index >= len(rainbow):
                    index = len(rainbow) - 1
                output[i] = [rainbow[index][0], rainbow[index][1], rainbow[index][2]]
                self.colormap[i] = output[i]
        else:
            print("")
            for i in range(len(self.colormap)): 
                for j in range(3):
                    self.colormap[i][j] -= 35
                    if self.colormap[i][j] < 0:
                        self.colormap[i][j] = 0
            output[i] = [self.colormap[i][0], self.colormap[i][1], self.colormap[i][2]]
        return output
