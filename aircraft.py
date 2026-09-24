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
        self.hp_desc = hp_desc            # m   (convertido desde ft en la tabla)
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
        name='B767',
        mlw=
        ...
    ),
    # los otros cuatro
}