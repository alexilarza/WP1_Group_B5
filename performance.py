"""
Aircraft performance in descent: thrust, minimum-RoD speed, rate of descent
and fuel flow.

Model: BADA 3.10 (SoW, Annex A).

Assumptions:
  - small descent angle -> L = m g  (same hypothesis used to derive v_min_rod)
  - thrust aligned with the flight path, no wind
  - parabolic drag polar: CD = CD0 + CD2 * CL^2
  - always clean configuration: the IAF is at 6000 ft and the simulation
    goes upwards from there, so the approach configuration is never reached

Units: SI everywhere, except inside the BADA formulas that require
ft (thrust) and kt / kN / min (fuel flow). Those conversions are done
inside each function.
"""

import math
from atmosphere import isa
from aircraft import FT_TO_M, KT_TO_MS

G = 9.80665   # m/s^2


# ---------------------------------------------------------------------------
# Thrust
# ---------------------------------------------------------------------------
def max_thrust(h, aircraft):
    """
    Maximum climb thrust [N] at altitude h [m].

    BADA formula: T_max = CT1 (1 - hp/CT2 + CT3 hp^2)
    CT2 is in ft and CT3 in 1/ft^2, so hp MUST be in feet here.
    """
    hp_ft = h / FT_TO_M

    T_max = aircraft.ct1 * (1 - hp_ft / aircraft.ct2 + aircraft.ct3 * hp_ft ** 2)

    return T_max


def idle_thrust(h, aircraft):
    """
    Descent (idle) thrust [N] at altitude h [m], clean configuration.

    Above hp_desc -> CT_desc_high, below -> CT_desc_low.
    Both h and aircraft.hp_desc are in metres.
    """
    if h > aircraft.hp_desc:
        coef = aircraft.ct_desc_high
    else:
        coef = aircraft.ct_desc_low

    T = coef * max_thrust(h, aircraft)

    return T


# ---------------------------------------------------------------------------
# Speed and rate of descent
# ---------------------------------------------------------------------------
def v_min_rod(m, rho, T, aircraft):
    """
    Speed [m/s] that minimises the rate of descent.

    Obtained by setting d(RoD)/dv = 0:
        3A v^4 - T v^2 - B = 0
    with
        A = 1/2 rho S CD0            (parasite drag:  D_p = A v^2)
        B = 2 CD2 (m g)^2 / (rho S)  (induced drag:   D_i = B / v^2)
    Biquadratic equation. The only positive root is:
        v^2 = (T + sqrt(T^2 + 12 A B)) / (6 A)
    """
    S = aircraft.S
    CD0 = aircraft.cd0_clean
    CD2 = aircraft.cd2_clean

    A = 0.5 * rho * S * CD0
    B = 2 * CD2 * (m * G) ** 2 / (rho * S)

    v_squared = (T + math.sqrt(T ** 2 + 12 * A * B)) / (6 * A)
    v = math.sqrt(v_squared)

    return v


def rate_of_descent(v, m, rho, T, aircraft):
    """
    Rate of descent [m/s] at speed v (positive when descending).

        CL  = 2 m g / (rho v^2 S)
        CD  = CD0 + CD2 CL^2
        D   = 1/2 rho v^2 S CD
        RoD = v (D - T) / (m g)
    """
    S = aircraft.S
    CD0 = aircraft.cd0_clean
    CD2 = aircraft.cd2_clean

    CL = 2 * m * G / (rho * v ** 2 * S)
    CD = CD0 + CD2 * CL ** 2
    D = 0.5 * rho * v ** 2 * S * CD

    rod = v * (D - T) / (m * G)

    return rod


# ---------------------------------------------------------------------------
# Fuel
# ---------------------------------------------------------------------------
def fuel_flow(T, v, aircraft):
    """
    Fuel flow [kg/s].

    BADA formulas: eta = CF1 (1 + v/CF2)   [kg/(min kN)], with v in kt
                   FF  = eta * T           [kg/min],      with T in kN
    """
    v_kt = v / KT_TO_MS
    T_kN = T / 1000

    eta = aircraft.cf1 * (1 + v_kt / aircraft.cf2)   # kg/(min kN)
    ff_per_min = eta * T_kN                          # kg/min
    ff = ff_per_min / 60                             # kg/s

    return ff


# ---------------------------------------------------------------------------
# Full flight state at one point of the trajectory
# ---------------------------------------------------------------------------
def descent_state(h, m, aircraft):
    """
    Flight state at altitude h [m] with mass m [kg].

    Returns a dictionary with:
        v      true airspeed [m/s]
        rod    rate of descent [m/s]
        gamma  descent angle [rad]
        T      idle thrust [N]
        ff     fuel flow [kg/s]
    """
    rho = isa(h)
    T = idle_thrust(h, aircraft)
    v = v_min_rod(m, rho, T, aircraft)
    rod = rate_of_descent(v, m, rho, T, aircraft)
    ff = fuel_flow(T, v, aircraft)

    # If thrust >= drag the aircraft would not descend: something is wrong
    if rod <= 0:
        print("WARNING:", aircraft.name, "does not descend at h =", h, "m. Check thrust.")

    gamma = math.asin(rod / v)

    state = {
        "v": v,
        "rod": rod,
        "gamma": gamma,
        "T": T,
        "ff": ff,
    }

    return state


# ---------------------------------------------------------------------------
# Validation. Only runs with: python performance.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from aircraft import AIRCRAFT

    b737 = AIRCRAFT["B737"]
    m = b737.mlw
    h = 6000 * FT_TO_M
    rho = isa(h)
    T = idle_thrust(h, b737)

    # Test 1: v_min_rod against brute force
    v = v_min_rod(m, rho, T, b737)
    v_best = 30.0
    rod_best = rate_of_descent(30.0, m, rho, T, b737)
    for i in range(30000):
        v_try = 30.0 + 0.01 * i
        rod_try = rate_of_descent(v_try, m, rho, T, b737)
        if rod_try < rod_best:
            rod_best = rod_try
            v_best = v_try
    print("Test 1: B737, 100% MLW, at the IAF")
    print("  formula:     v =", round(v, 2), "m/s")
    print("  brute force: v =", round(v_best, 2), "m/s  (must match)")

    # Test 2: with T = 0 -> CL = sqrt(3 CD0 / CD2)
    v0 = v_min_rod(m, rho, 0.0, b737)
    CL0 = 2 * m * G / (rho * v0 ** 2 * b737.S)
    print()
    print("Test 2: with T = 0")
    print("  CL obtained       =", round(CL0, 4))
    print("  sqrt(3 CD0 / CD2) =", round(math.sqrt(3 * b737.cd0_clean / b737.cd2_clean), 4), "(must match)")

    # Test 3: full state of every aircraft at the IAF and at FL400
    print()
    print("Test 3: state at 100% MLW (check the numbers look reasonable)")
    print("aircraft  h[ft]   v[kt]   RoD[ft/min]  gamma[deg]  T[kN]  FF[kg/h]")
    for name in AIRCRAFT:
        ac = AIRCRAFT[name]
        for h_ft in [6000, 40000]:
            s = descent_state(h_ft * FT_TO_M, ac.mlw, ac)
            print(name, "   ", h_ft,
                  "  ", round(s["v"] / KT_TO_MS),
                  "    ", round(s["rod"] / FT_TO_M * 60),
                  "       ", round(math.degrees(s["gamma"]), 2),
                  "     ", round(s["T"] / 1000, 1),
                  "  ", round(s["ff"] * 3600))