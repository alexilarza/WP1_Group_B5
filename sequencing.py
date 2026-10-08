"""
Arrival sequencing at LEBL RWY 24L (SoW v1.1, section 3).

Scenario 1: all aircraft reach the first waypoint of their STAR at 11:45:00.
Scenario 2: consecutive aircraft reach the IAF exactly 2 minutes apart,
            keeping the order of scenario 1 and without moving the first one.

The trajectories come from main.py (dictionary "trajectories").
Times of day are stored in seconds since midnight. Units: SI.
"""

ENTRY_TIME = 11 * 3600 + 45 * 60     # 11:45:00 in seconds since midnight
SEPARATION = 120.0                   # s   separation at the IAF in scenario 2

# ---------------------------------------------------------------------------
# Arrivals (SoW v1.1, section 3)
# distance_km: distance ALONG THE STAR from its first waypoint to the IAF [km],
# from the ENAIRE STAR charts (AIP; the charts give NM, converted to km).
# ---------------------------------------------------------------------------
STARS = {
    "ALBER1Z": {"aircraft": "B767", "mlw": 80,  "distance_km": 91.7},
    "PUMAL1Z": {"aircraft": "B737", "mlw": 100, "distance_km": 94.5},
    "MARTA3Z": {"aircraft": "B777", "mlw": 100, "distance_km": 178.3},
    "MATEX3Z": {"aircraft": "B767", "mlw": 80,  "distance_km": 190.0},
    "LOBAR2W": {"aircraft": "A319", "mlw": 80,  "distance_km": 151.4},
    "CASPE2W": {"aircraft": "A320", "mlw": 100, "distance_km": 164.0},
}


def time_to_string(seconds):
    """Converts seconds since midnight to the text HH:MM:SS."""
    seconds = round(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(secs).zfill(2)


def duration_to_string(seconds):
    """Converts a duration in seconds to the text 'MM min SS s'."""
    seconds = round(seconds)
    minutes = seconds // 60
    secs = seconds % 60
    return str(minutes) + " min " + str(secs).zfill(2) + " s"


def time_to_iaf(trajectory, distance):
    """
    Finds the point of the trajectory that is "distance" metres before the IAF.

    Returns:
        flight_time  time from that point to the IAF [s]
        h_entry      altitude at that point [m]

    The trajectory has one point per second, so the result is accurate to 1 s.
    """
    x = trajectory["x"]
    t = trajectory["t"]
    h = trajectory["h"]

    for i in range(len(x)):
        if x[i] <= -distance:
            flight_time = -t[i]
            h_entry = h[i]
            return flight_time, h_entry

    # If we get here the STAR is longer than the whole CDO from FL400
    print("WARNING: STAR longer than the CDO from FL400. Result not valid.")
    return -t[-1], h[-1]


# ---------------------------------------------------------------------------
# Scenario 1
# ---------------------------------------------------------------------------
def scenario_1(trajectories):
    """
    All aircraft at the STAR entry point at 11:45:00.
    Returns a dictionary: results["ALBER1Z"] -> h_entry, flight_time,
    entry_time, iaf_time.
    """
    results = {}

    for star in STARS:
        data = STARS[star]

        if data["distance_km"] is None:
            print("Missing STAR distance for", star, "-> skipped")
            continue

        trajectory = trajectories[data["aircraft"], data["mlw"]]
        distance = data["distance_km"] * 1000          # km -> m
        flight_time, h_entry = time_to_iaf(trajectory, distance)

        results[star] = {
            "h_entry": h_entry,                        # m
            "flight_time": flight_time,                # s
            "entry_time": ENTRY_TIME,                  # s since midnight
            "iaf_time": ENTRY_TIME + flight_time,      # s since midnight
        }

    return results


def arrival_order(results):
    """
    Returns the list of STARs ordered by arrival time at the IAF.

    Builds a list of [iaf_time, star] pairs and sorts it: Python sorts
    lists of pairs by their first element, i.e. by the time.
    """
    pairs = []
    for star in results:
        pairs.append([results[star]["iaf_time"], star])

    pairs.sort()

    order = []
    for pair in pairs:
        order.append(pair[1])

    return order


# ---------------------------------------------------------------------------
# Scenario 2
# ---------------------------------------------------------------------------
def scenario_2(results_1, order):
    """
    Same order of arrival as scenario 1, exactly SEPARATION seconds between
    consecutive aircraft at the IAF. The first aircraft is not moved.

    The flight time from the STAR entry to the IAF does not change (same
    trajectory, same distance): only the entry time is moved.
    """
    first_star = order[0]
    first_iaf_time = results_1[first_star]["iaf_time"]

    results_2 = {}

    for k in range(len(order)):
        star = order[k]
        flight_time = results_1[star]["flight_time"]

        iaf_time = first_iaf_time + k * SEPARATION     # k-th aircraft: k x 2 min later
        entry_time = iaf_time - flight_time            # go back the flight time
        shift = entry_time - ENTRY_TIME                # > 0 delayed, < 0 advanced

        results_2[star] = {
            "h_entry": results_1[star]["h_entry"],
            "flight_time": flight_time,
            "entry_time": entry_time,
            "iaf_time": iaf_time,
            "shift": shift,
        }

    return results_2


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------
def print_scenario(results, order, title):
    """Prints one row per aircraft, in order of arrival at the IAF."""
    print()
    print(title)
    print("STAR      aircraft  MLW%  h_entry[m]  entry     STAR->IAF     IAF       gap[s]")

    for k in range(len(order)):
        star = order[k]
        r = results[star]

        if k == 0:
            gap = "-"
        else:
            previous = order[k - 1]
            gap = round(r["iaf_time"] - results[previous]["iaf_time"])

        print(star, "  ", STARS[star]["aircraft"], "    ", STARS[star]["mlw"],
              "   ", round(r["h_entry"]),
              "      ", time_to_string(r["entry_time"]),
              "", duration_to_string(r["flight_time"]),
              "", time_to_string(r["iaf_time"]),
              "", gap)