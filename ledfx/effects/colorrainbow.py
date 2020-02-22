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

    def apply_rainbow(self, y):
        output = np.zeros(shape=(self.pixel_count, 3))
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
            output[i] = [rainbow[index][0]*y, rainbow[index][1]*y, rainbow[index][2]*y]
        return output
