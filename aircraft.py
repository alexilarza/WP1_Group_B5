FT_TO_M = 0.3048
KT_TO_MS = 0.514444

class Aircraft:
    def __init__(self, name, mlw, mtow, max_payload, S,
                 cd0_clean, cd2_clean, cd0_app, cd2_app,
                 hp_desc, ct_desc_high, ct_desc_low, ct_desc_app,
                 ct1, ct2, ct3, cf1, cf2):
        self.name = name
        self.mlw = mlw                    # kg
        self.mtow = mtow                  # kg  (no usado en WP1)
        self.max_payload = max_payload    # kg  (no usado en WP1)
        self.S = S                        # m^2
        self.cd0_clean = cd0_clean        # -
        self.cd2_clean = cd2_clean        # -
        self.cd0_app = cd0_app            # -   (no usado: IAF a 6000 ft)
        self.cd2_app = cd2_app            # -   (no usado)
        self.hp_desc = hp_desc            # converted to m
        self.ct_desc_high = ct_desc_high  # -
        self.ct_desc_low = ct_desc_low    # -
        self.ct_desc_app = ct_desc_app    # -   (no usado)
        self.ct1 = ct1                    # N
        self.ct2 = ct2                    # ft  -- NO convertir
        self.ct3 = ct3                    # 1/ft^2 -- NO convertir
        self.cf1 = cf1                    # kg/(min*kN) -- NO convertir
        self.cf2 = cf2                    # kt -- NO convertir


AIRCRAFT = {
    "B767": Aircraft(
        name="B767",
        mlw=145.15e3, mtow=204.10e3, max_payload=46.50e3, S=283.50,
        cd0_clean=0.01740, cd2_clean=0.04590,
        cd0_app=0.01400,   cd2_app=0.04900,
        hp_desc=26418 * FT_TO_M, # Converted to m
        ct_desc_high=0.064359, ct_desc_low=0.055988, ct_desc_app=0.12475,
        ct1=351670, ct2=44673, ct3=1.0129e-10,
        cf1=0.54005, cf2=557.82),

    "B777": Aircraft(
        name="B777",
        mlw=237.68e3, mtow=299.30e3, max_payload=64.90e3, S=428.04,
        cd0_clean=0.01570, cd2_clean=0.04200,
        cd0_app=0.01730,   cd2_app=0.04840,
        hp_desc=36122 * FT_TO_M, # Converted to m
        ct_desc_high=0.044239, ct_desc_low=0.041065, ct_desc_app=0.092921,
        ct1=425770, ct2=48987, ct3=6.6146e-11,
        cf1=0.87843, cf2=3689.7),

    "B737": Aircraft(
        name="B737",
        mlw=51.71e3, mtow=70.80e3, max_payload=16.92e3, S=124.65,
        cd0_clean=0.02350, cd2_clean=0.04450,
        cd0_app=0.02700,   cd2_app=0.04410,
        hp_desc=30152 * FT_TO_M, # Converted to m
        ct_desc_high=0.036336, ct_desc_low=0.053395, ct_desc_app=0.16440,
        ct1=145730, ct2=55638, ct3=1.4200e-11,
        cf1=0.94680, cf2=1.0e14),

    "A320": Aircraft(
        name="A320",
        mlw=64.50e3, mtow=77.00e3, max_payload=21.50e3, S=122.60,
        cd0_clean=0.02400, cd2_clean=0.03750,
        cd0_app=0.02420,   cd2_app=0.04690,
        hp_desc=12398 * FT_TO_M, # Converted to m
        ct_desc_high=0.045711, ct_desc_low=0.027207, ct_desc_app=0.13981,
        ct1=136050, ct2=52238, ct3=2.6637e-11,
        cf1=0.94000, cf2=1.0e5),

    "A319": Aircraft(
        name="A319",
        mlw=61.00e3, mtow=70.00e3, max_payload=17.00e3, S=122.60,
        cd0_clean=0.02800, cd2_clean=0.03100,
        cd0_app=0.02840,   cd2_app=0.03760,
        hp_desc=27726 * FT_TO_M, # Converted to m
        ct_desc_high=0.083084, ct_desc_low=0.051765, ct_desc_app=0.14767,
        ct1=139000, ct2=58900, ct3=5.7200e-15,
        cf1=0.68800, cf2=1670.0),
}