import math
from atmosphere import isa                      # assumed: isa(h_m) -> (T, p, rho)
from aircraft import FT_TO_M, KT_TO_MS

G0 = 9.80665


def max_thrust(ac, h):
    """BADA max climb thrust [N]. h in m; BADA formula needs ft."""
    hp = h / FT_TO_M
    return ac.ct1 * (1 - hp / ac.ct2 + ac.ct3 * hp**2)


def idle_thrust(ac, h):
    """BADA descent thrust [N], clean configuration (valid above 6000 ft)."""
    coef = ac.ct_desc_high if h > ac.hp_desc else ac.ct_desc_low   # m vs m
    return coef * max_thrust(ac, h)


def v_min_rod(ac, m, rho):
    """TAS [m/s] that minimises rate of descent at idle thrust."""
    return math.sqrt(2 * m * G0 / (rho * ac.S)
                     * math.sqrt(ac.cd2_clean / (3 * ac.cd0_clean)))


def drag(ac, m, v, rho, cos_gamma=1.0):
    q = 0.5 * rho * v**2
    cl = m * G0 * cos_gamma / (q * ac.S)
    cd = ac.cd0_clean + ac.cd2_clean * cl**2
    return q * ac.S * cd


def fuel_flow(ac, T, v):
    """FF [kg/s]. eta in kg/(min*kN) with v in kt; T in N."""
    eta = ac.cf1 * (1 + (v / KT_TO_MS) / ac.cf2)
    return eta * (T / 1000) / 60


def descent_state(ac, m, h):
    """Flight state at altitude h [m], mass m [kg]. Returns v, gamma, rod, ff."""
    rho = isa(h)
    v = v_min_rod(ac, m, rho)
    T = idle_thrust(ac, h)

    gamma = 0.0
    for _ in range(3):                           # cos(gamma) couples D and gamma
        D = drag(ac, m, v, rho, math.cos(gamma))
        gamma = math.asin((D - T) / (m * G0))

    if gamma <= 0:
        raise ValueError(f"{ac.name}: thrust >= drag at h={h:.0f} m, no descent")

    return {
        "v": v,                                  # TAS [m/s]
        "gamma": gamma,                          # [rad]
        "rod": v * math.sin(gamma),              # [m/s]
        "ff": fuel_flow(ac, T, v),               # [kg/s]
        "T": T                                   # idle thrust [N]
    }