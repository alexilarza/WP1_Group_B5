"""
atmosphere.py
-------------
Modelo de la Atmosfera Estandar Internacional (ISA).
Devuelve la densidad del aire a una altitud dada.

Valido entre 0 y 20 000 m. El simulador va de 1829 m (IAF, 6000 ft)
a 12 192 m (FL400), asi que siempre estamos dentro de ese rango.

Referencia: M. Cavcar, "The International Standard Atmosphere (ISA)",
ecuaciones (1), (7), (8) y (9).

Unidades: altitud en m, temperatura en K, presion en Pa, densidad en kg/m^3.
"""

import math

# ---------------------------------------------------------------------------
# Constantes (todas de Cavcar, en SI)
# ---------------------------------------------------------------------------
T0 = 288.15          # K         temperatura a nivel del mar
P0 = 101325.0        # Pa        presion a nivel del mar
LAMBDA = 0.0065      # K/m       gradiente termico en la troposfera
R = 287.04           # J/(kg K)  constante del aire
G = 9.80665          # m/s^2     gravedad estandar
EXP_TROPO = 5.2561   # -         exponente de la ec. (7)

H11 = 11000.0        # m         altitud de la tropopausa
T11 = 216.65         # K         temperatura en la tropopausa
P11 = 22632.0        # Pa        presion en la tropopausa (226.32 hPa)

H_MIN = 0.0          # m         limite inferior del modelo
H_MAX = 20000.0      # m         limite superior del modelo


def isa(h):
    """
    Devuelve la densidad del aire [kg/m^3] a la altitud h [m].
    """

    # --- 1. Avisar si la altitud esta fuera del rango del modelo ---
    # El calculo sigue igualmente, pero el mensaje te indica que algo va mal
    # en el bucle (error de signo o altitud en pies en vez de metros).
    if h < H_MIN:
        print("AVISO: altitud negativa:", h, "m. Revisa el bucle.")

    if h > H_MAX:
        print("AVISO: altitud por encima de 20000 m:", h, "m. Revisa las unidades.")

    # --- 2. Temperatura y presion segun la capa ---
    if h <= H11:
        # Troposfera
        T = T0 - LAMBDA * h                               # Cavcar ec. (1)
        p = P0 * (1 - LAMBDA * h / T0) ** EXP_TROPO       # Cavcar ec. (7)
    else:
        # Estratosfera: temperatura constante.
        # La presion parte de la tropopausa (P11), no del nivel del mar.
        T = T11
        p = P11 * math.exp(-G / (R * T11) * (h - H11))    # Cavcar ec. (8)

    # --- 3. Densidad con la ley de gases ideales ---
    rho = p / (R * T)                                     # Cavcar ec. (9)

    return rho


# ---------------------------------------------------------------------------
# Validacion contra la Tabla 3 de Cavcar.
# Solo se ejecuta si lanzas este archivo directamente: python atmosphere.py
# Si otro archivo hace "from atmosphere import isa", esto NO se ejecuta.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    FT_TO_M = 0.3048
    RHO0 = 1.225   # densidad a nivel del mar, para pasar sigma a rho

    print("Altitud            rho calculada    rho Cavcar")
    print("-----------------------------------------------")

    rho = isa(0.0)
    print("0 ft               ", round(rho, 4), "          ", RHO0)

    rho = isa(6000 * FT_TO_M)
    print("6000 ft (IAF)      ", round(rho, 4), "          ", round(0.8359 * RHO0, 4))

    rho = isa(30000 * FT_TO_M)
    print("30000 ft           ", round(rho, 4), "          ", round(0.3741 * RHO0, 4))

    rho = isa(40000 * FT_TO_M)
    print("40000 ft (FL400)   ", round(rho, 4), "          ", round(0.2462 * RHO0, 4))

    # Las dos capas deben dar casi lo mismo justo debajo y justo encima de 11 000 m
    print()
    print("Continuidad en la tropopausa:")
    print("  10999 m:", round(isa(10999.0), 5))
    print("  11001 m:", round(isa(11001.0), 5))
