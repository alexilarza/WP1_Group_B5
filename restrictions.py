"""
STAR altitude restrictions at LEBL RWY 24L (SoW v1.1, section 4).

Each restriction is stored as a minimum and/or maximum altitude at a
waypoint of the STAR. This covers every type of restriction on the chart:
    AT       FL150         -> alt_min = alt_max = FL150
    AT/ABOVE FL150 or more -> alt_min = FL150, alt_max = None
    AT/BELOW FL150 or less -> alt_min = None,  alt_max = FL150
    WINDOW   FL120-FL150   -> alt_min = FL120, alt_max = FL150

Data from the ENAIRE STAR charts (AIP, AD 2-LEBL STAR 3).
Altitudes are given in ft on the chart and converted to m here.
"""

from aircraft import FT_TO_M
from sequencing import STARS, time_to_iaf


class Restriction:
    def __init__(self, waypoint, distance_km, alt_min, alt_max):
        self.waypoint = waypoint          # name of the waypoint
        self.distance_km = distance_km    # km  distance along the STAR from the waypoint to the IAF
        self.alt_min = alt_min            # m   minimum altitude (None if no minimum)
        self.alt_max = alt_max            # m   maximum altitude (None if no maximum)


# ---------------------------------------------------------------------------
# Restrictions of each STAR (AIP ENAIRE, AD 2-LEBL STAR 3).
# Restriction(waypoint, distance to the IAF [km], minimum [m], maximum [m])
# Waypoints without restriction are included to see the simulated altitude.
# ---------------------------------------------------------------------------
RESTRICTIONS = {
    "ALBER1Z": [
        Restriction("ALBER", 129.1, 11000 * FT_TO_M, 25000 * FT_TO_M),  # FL110 - FL250
        Restriction("CUTXE",  93.0, None, None),
        Restriction("UTHAN",  51.5, None, None),
        Restriction("ENJUC",  32.0,  8000 * FT_TO_M, None),             # FL080 or above
        Restriction("UCREQ",  19.3, None, 10000 * FT_TO_M),             # FL100 or below
        Restriction("SLL",     0.0,  6000 * FT_TO_M, None),             # 6000 ft or above
    ],
    "PUMAL1Z": [
        Restriction("PUMAL", 94.5, 13000 * FT_TO_M, 25000 * FT_TO_M),   # FL130 - FL250
        Restriction("BERGA", 72.6, 12000 * FT_TO_M, None),              # FL120 or above
        Restriction("KOSIT", 46.3, None, None),
        Restriction("MAMUK", 35.4,  8000 * FT_TO_M, None),              # FL080 or above
        Restriction("UCREQ", 19.2, None, 10000 * FT_TO_M),              # FL100 or below
        Restriction("SLL",    0.0,  6000 * FT_TO_M, None),              # 6000 ft or above
    ],
    "MARTA3Z": [
        Restriction("MARTA", 178.3, None, 24000 * FT_TO_M),             # FL240 or below
        Restriction("EBROX", 138.9, 10000 * FT_TO_M, None),             # FL100 or above
        Restriction("RES",    90.2, None, None),
        Restriction("VLA",    51.0, None, None),
        Restriction("BL463",  18.5, None, 10000 * FT_TO_M),             # FL100 or below
        Restriction("SLL",     0.0,  6000 * FT_TO_M, None),             # 6000 ft or above
    ],
    "MATEX3Z": [
        Restriction("MATEX", 190.0, None, 28000 * FT_TO_M),             # FL280 or below
        Restriction("SENIA", 137.0, 10000 * FT_TO_M, None),             # FL100 or above
        Restriction("RES",    90.2, None, None),
        Restriction("VLA",    50.9, None, None),
        Restriction("BL463",  18.5, None, 10000 * FT_TO_M),             # FL100 or below
        Restriction("SLL",     0.0,  6000 * FT_TO_M, None),             # 6000 ft or above
    ],
    "LOBAR2W": [
        Restriction("LOBAR", 151.4, None, 28000 * FT_TO_M),             # FL280 or below
        Restriction("PEKIS",  83.4, 16000 * FT_TO_M, 20000 * FT_TO_M),  # FL160 - FL200
        Restriction("BL461",  18.5, 10000 * FT_TO_M, None),             # FL100 or above
        Restriction("SLL",     0.0,  6000 * FT_TO_M, None),             # 6000 ft or above
    ],
    "CASPE2W": [
        Restriction("CASPE", 164.0, None, 28000 * FT_TO_M),             # FL280 or below
        Restriction("MECUH",  88.2, 16000 * FT_TO_M, 20000 * FT_TO_M),  # FL160 - FL200
        Restriction("VIBOK",  51.0, None, 15000 * FT_TO_M),             # FL150 or below
        Restriction("BL461",  18.5, None, 10000 * FT_TO_M),             # FL100 or below
        Restriction("SLL",     0.0,  6000 * FT_TO_M, None),             # 6000 ft or above
    ],
}


def check_restrictions(trajectories):
    """
    For every restriction, finds the altitude of the simulated trajectory at
    that waypoint and checks whether it complies.

    Prints, for each waypoint: simulated altitude, limits and the result.
    The deviation is how many metres the trajectory is outside the limit.
    """
    print()
    print("STAR ALTITUDE RESTRICTIONS")
    print("STAR      waypoint  dist[km]  h_sim[m]  min[m]  max[m]  result")

    for star in RESTRICTIONS:
        data = STARS[star]
        trajectory = trajectories[data["aircraft"], data["mlw"]]

        for r in RESTRICTIONS[star]:
            # Altitude of the CDO trajectory at this waypoint
            flight_time, h_sim = time_to_iaf(trajectory, r.distance_km * 1000)

            if r.alt_min is None and r.alt_max is None:
                result = "no restriction"
            elif r.alt_min is not None and h_sim < r.alt_min:
                result = "TOO LOW by " + str(round(r.alt_min - h_sim)) + " m"
            elif r.alt_max is not None and h_sim > r.alt_max:
                result = "TOO HIGH by " + str(round(h_sim - r.alt_max)) + " m"
            else:
                result = "OK"

            if r.alt_min is None:
                min_text = "-"
            else:
                min_text = round(r.alt_min)

            if r.alt_max is None:
                max_text = "-"
            else:
                max_text = round(r.alt_max)

            print(star, "  ", r.waypoint,
                  "   ", r.distance_km,
                  "    ", round(h_sim),
                  "   ", min_text,
                  "  ", max_text,
                  "  ", result)