"""
Model of International Standard Atmosphere (ISA).
Gives back air density at a given altitude.

Valid between 0 and 20000m. The range of the project goes within it.

Reference: M. Cavcar, "The International Standard Atmosphere (ISA)",
equations (1), (7), (8) and (9).

Units: altitude in m, temperature in K, pressure in Pa, density in kg/m^3.
"""

import math

T0 = 288.15          # K         Temperature at sea level
P0 = 101325.0        # Pa        Pressure at sea level
LAMBDA = 0.0065      # K/m       Thermal gradient in the atmosphere
R = 287.04           # J/(kg K)  Air specific gas constant
G = 9.80665          # m/s^2     SStandand gravity parameter
EXP_TROPO = 5.2561   # -         Exponent in the (7) equation

H11 = 11000.0        # m         Tropopause altitude
T11 = 216.65         # K         Tropopause temperature
P11 = 22632.0        # Pa        Tropopause pressure (226.32 hPa)

H_MIN = 0.0          # m         Inferior model limit
H_MAX = 20000.0      # m         Superior model limit


def isa(h):
    """
    Returns air density [kg/m^3] at altitude h [m].
    """

    # Tells if altitude is not in the range
    if h < H_MIN:
        print("AVISO: altitud negativa:", h, "m. Revisa el bucle.")

    if h > H_MAX:
        print("AVISO: altitud por encima de 20000 m:", h, "m. Revisa las unidades.")

    # Temperature and pressure in troposphere and stratosphere
    if h <= H11:
        # Troposphere
        T = T0 - LAMBDA * h                               # Cavcar ec. (1)
        p = P0 * (1 - LAMBDA * h / T0) ** EXP_TROPO       # Cavcar ec. (7)
    else:
        # Stratosphere: temperature constant.

        T = T11
        p = P11 * math.exp(-G / (R * T11) * (h - H11))    # Cavcar ec. (8)

    # Density for an ideal gas
    rho = p / (R * T)                                     # Cavcar ec. (9)

    return rho
