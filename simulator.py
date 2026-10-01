"""
CDO trajectory simulator.

The trajectory is simulated BACKWARDS in time: it starts at the Initial
Approach Fix (IAF), where the weight is known (a percentage of the MLW),
and goes up until FL400. This is done because the weight at the Top of
Descent is unknown (WP1 Simulator development slides, 6-7).

Coordinates:
  x = 0 at the IAF, negative before it (the aircraft is still far away)
  h = altitude above sea level
  t = 0 at the IAF, negative before it

Units: SI (m, s, kg, m/s).
"""

import math
from aircraft import AIRCRAFT, FT_TO_M
from performance import descent_state

H_IAF = 6000 * FT_TO_M     # m   altitude at the IAF (confirmed by the professor)
H_TOP = 40000 * FT_TO_M    # m   FL400, end of the backward simulation
DT = 1.0                   # s   duration of each iteration


def simulate_cdo(aircraft_model, MLW_percent):
    """
    Simulates the CDO backwards from the IAF to FL400.

    Returns a dictionary of lists, one value per second:
        x    distance to the IAF [m]   (negative)
        h    altitude [m]
        t    time to the IAF [s]       (negative)
        m    mass [kg]
        v    true airspeed [m/s]
        rod  rate of descent [m/s]
    """
    aircraft = AIRCRAFT[aircraft_model]

    # --- Initial conditions: the aircraft at the IAF ---
    x = 0.0
    h = H_IAF
    t = 0.0
    m = aircraft.mlw * MLW_percent / 100

    # --- Lists where every point of the trajectory is stored ---
    x_list = []
    h_list = []
    t_list = []
    m_list = []
    v_list = []
    rod_list = []

    # --- Backward loop: one iteration = one second ---
    while h < H_TOP:
        # Flight state at the current point (speed constant within the iteration)
        state = descent_state(h, m, aircraft)
        v = state["v"]
        rod = state["rod"]
        gamma = state["gamma"]
        ff = state["ff"]

        # Store the current point
        x_list.append(x)
        h_list.append(h)
        t_list.append(t)
        m_list.append(m)
        v_list.append(v)
        rod_list.append(rod)

        # Go one second back in time:
        h = h + rod * DT                          # the aircraft was HIGHER
        x = x - v * math.cos(gamma) * DT          # the aircraft was FURTHER away
        m = m + ff * DT                           # the aircraft was HEAVIER (fuel not burnt yet)
        t = t - DT

    # Store the last point (first point at or above FL400)
    x_list.append(x)
    h_list.append(h)
    t_list.append(t)
    m_list.append(m)
    v_list.append(v)
    rod_list.append(rod)

    trajectory = {
        "x": x_list,
        "h": h_list,
        "t": t_list,
        "m": m_list,
        "v": v_list,
        "rod": rod_list,
    }

    return trajectory


def getCDO(aircraft_model, MLW_percent):
    """
    Mandatory function of the SoW: [x, h] = getCDO(aircraft_model, MLW_percent)

    aircraft_model: "B767", "B777", "B737", "A320" or "A319"
    MLW_percent:    weight at the IAF as a percentage of the MLW (80 or 100)

    Returns two lists: x [m] and h [m].
    """
    trajectory = simulate_cdo(aircraft_model, MLW_percent)

    return trajectory["x"], trajectory["h"]


# ---------------------------------------------------------------------------
# Validation. Only runs with: python simulator.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("aircraft  MLW%   distance[km]  time[min]  mass IAF[kg]  mass TOD[kg]  fuel[kg]  h_last[m]")
    for name in AIRCRAFT:
        for pct in [80, 100]:
            traj = simulate_cdo(name, pct)
            distance = -traj["x"][-1] / 1000
            time = -traj["t"][-1] / 60
            m_iaf = traj["m"][0]
            m_tod = traj["m"][-1]
            fuel = m_tod - m_iaf
            print(name, "    ", pct,
                  "     ", round(distance, 1),
                  "       ", round(time, 1),
                  "     ", round(m_iaf),
                  "       ", round(m_tod),
                  "      ", round(fuel),
                  "     ", round(traj["h"][-1], 1))

    # Check that getCDO returns what the SoW asks for
    x, h = getCDO("B767", 100)
    print()
    print("getCDO('B767', 100): first point x =", x[0], "m, h =", round(h[0], 1), "m")
    print("                     last point  x =", round(x[-1]), "m, h =", round(h[-1], 1), "m")
    print("                     number of points =", len(x))