"""
Main script of WP1: generates all the CDO trajectories with a single click
and plots them.

Run with: python main.py

All trajectories are stored in the dictionary "trajectories" so they can be
reused in later tasks (arrival sequencing, STAR altitude constraints).
"""

import matplotlib.pyplot as plt
from aircraft import AIRCRAFT, FT_TO_M
from simulator import getCDO, simulate_cdo
from sequencing import STARS, scenario_1, scenario_2, arrival_order, print_scenario, time_to_string
from restrictions import check_restrictions, check_all_aircraft

MLW_PERCENTS = [80, 100]

# One colour per aircraft (checked for colour-blind readers),
# one line style per weight: solid = 100% MLW, dashed = 80% MLW.
COLOURS = {
    "B767": "#2a78d6",   # blue
    "B777": "#eb6834",   # orange
    "B737": "#1baf7a",   # aqua
    "A320": "#eda100",   # yellow
    "A319": "#e87ba4",   # pink
}
LINE_STYLES = {
    100: "-",
    80: "--",
}


# ---------------------------------------------------------------------------
# 1. Compute every trajectory
# ---------------------------------------------------------------------------
# trajectories["B767", 100] -> dictionary with lists x, h, t, m, v, rod
trajectories = {}

for name in AIRCRAFT:
    for pct in MLW_PERCENTS:
        trajectories[name, pct] = simulate_cdo(name, pct)

# getCDO is the function required by the SoW. Example of use:
x_b767, h_b767 = getCDO("B767", 100)


# ---------------------------------------------------------------------------
# 2. Summary table in the console
# ---------------------------------------------------------------------------
print("aircraft  MLW%   distance[km]  time[min]  fuel[kg]")
for name in AIRCRAFT:
    for pct in MLW_PERCENTS:
        traj = trajectories[name, pct]
        distance = -traj["x"][-1] / 1000
        time = -traj["t"][-1] / 60
        fuel = traj["m"][-1] - traj["m"][0]
        print(name, "    ", pct,
              "     ", round(distance, 1),
              "       ", round(time, 1),
              "     ", round(fuel))


# ---------------------------------------------------------------------------
# 3. Arrival sequencing at LEBL (SoW section 3)
#    Needs the STAR distances in sequencing.py
# ---------------------------------------------------------------------------
results_1 = scenario_1(trajectories)
order = arrival_order(results_1)

# Only run the scenarios when all six STAR distances are filled in
if len(order) == len(STARS):
    print_scenario(results_1, order, "SCENARIO 1: all aircraft at the STAR entry point at 11:45:00")

    results_2 = scenario_2(results_1, order)
    print_scenario(results_2, order, "SCENARIO 2: 2 min separation at the IAF")

    print()
    print("Scenario 2: new STAR entry times")
    for star in order:
        print(star, "  ", time_to_string(results_2[star]["entry_time"]),
              "  change:", round(results_2[star]["shift"]), "s")
else:
    print("Fill in all the STAR distances in sequencing.py to run the scenarios.")


# ---------------------------------------------------------------------------
# 4. Compliance with the STAR altitude restrictions (SoW section 4)
#    Needs the restrictions in restrictions.py
# ---------------------------------------------------------------------------
check_restrictions(trajectories)

# Every STAR checked with all 10 trajectories, not only the assigned aircraft.
# If a STAR is longer than the CDO from FL400, the aircraft cruises at FL400
# until the top of descent (see time_to_iaf in sequencing.py).
check_all_aircraft(trajectories)


# ---------------------------------------------------------------------------
# 5. Plot: altitude vs distance to the IAF
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))

for name in AIRCRAFT:
    for pct in MLW_PERCENTS:
        traj = trajectories[name, pct]
        x_km = [x / 1000 for x in traj["x"]]
        ax.plot(x_km, traj["h"],
                color=COLOURS[name],
                linestyle=LINE_STYLES[pct],
                linewidth=2,
                label=name + " [" + str(pct) + "% MLW]")

# Reference lines: IAF altitude and FL400
ax.axhline(6000 * FT_TO_M, color="grey", linewidth=0.8, linestyle=":")
ax.axhline(40000 * FT_TO_M, color="grey", linewidth=0.8, linestyle=":")
ax.text(-205, 6000 * FT_TO_M + 150, "IAF (6000 ft)", ha="left", color="dimgrey", fontsize=9)
ax.text(-5, 40000 * FT_TO_M - 450, "FL400", ha="right", color="dimgrey", fontsize=9)

ax.set_xlabel("Distance to the IAF, x [km]")
ax.set_ylabel("Altitude, h [m]")
ax.set_title("CDO descent trajectories (idle thrust, minimum rate of descent, ISA)")
ax.grid(True, color="lightgrey", linewidth=0.5)
ax.legend(fontsize=9, ncol=2)

plt.tight_layout()
plt.savefig("cdo_trajectories.png", dpi=200)   # for the paper
plt.show()