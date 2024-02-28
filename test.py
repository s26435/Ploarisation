import numpy as np
import math

"""
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_polarization_processor import PolarizationProcessorSDK
"""


class Polarisation:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.quad_view = np.ones(shape=(height, width))  # TODO camera connection

    def __str__(self):
        return f"Polarisation=[height = {self.height}, width = {self.width}, quad_view]"

    def divide(self, table):
        if table.shape[0] % 2 != 0 or table.shape[1] % 2 != 0:
            raise ValueError("The dimensions of the array must be even numbers.")
        vertical = table[:table.shape[0] // 2, :table.shape[1] // 2]
        horizontal = table[:table.shape[0] // 2, table.shape[1] // 2:]
        negative_diagonal = table[table.shape[0] // 2:, :table.shape[1] // 2]
        diagonal = table[table.shape[0] // 2:, table.shape[1] // 2:]
        return vertical, horizontal, negative_diagonal, diagonal

    def calculate_sum(self, switch='zero'):
        vertical, horizontal, negative_diagonal, diagonal = self.divide(self.quad_view)
        sum_view = np.zeros(shape=(self.height // 2, self.width // 2))
        with np.nditer(sum_view, flags=['multi_index'], op_flags=['readwrite']) as it:
            while not it.finished:
                index = it.multi_index
                if switch == 'zero':
                    sum_view[index] = vertical[index] + horizontal[index] + negative_diagonal[index] + diagonal[index]
                elif switch == 'horizontal':
                    sum_view[index] = horizontal[index] - vertical[index]
                elif switch == 'diagonal':
                    sum_view[index] = diagonal[index] - negative_diagonal[index]
                else:
                    raise TypeError("Wrong switch value.")
                it.iternext()
        return sum_view

    def psi(self, horizontal, diagonal):
        if diagonal == 0:
            raise ValueError("Diagonal in psi variable is zero")
        return 0.5 * math.atan(diagonal / horizontal)

    def delta(self, zero, horizontal, diagonal, psi):
        return math.acos((horizontal * math.cos(2 * psi) + diagonal * math.sin(2 * psi)) / zero)

    def delta_view(self):
        sum_delta = np.zeros(shape=(self.height // 2, self.width // 2))
        sum_zero = self.calculate_sum()
        sum_hori = self.calculate_sum(switch='horizontal')
        sum_diag = self.calculate_sum(switch='diagonal')
        with np.nditer(sum_delta, flags=['multi_index'], op_flags=['readwrite']) as it:
            while not it.finished:
                index = it.multi_index
                zero, hori, diag = sum_zero[index], sum_hori[index], sum_diag[index],
                sum_delta[index] = self.delta(sum_zero[index], hori, diag, self.psi(hori, diag))
                print(sum_delta[index])
                it.iternext()


if __name__ == "__main__":
    polar = Polarisation(10, 10)
    polar.delta_view()
