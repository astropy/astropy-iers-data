import numpy as np

np.loadtxt(
    "data/eopc04.1962-now",
    dtype=[
        ("year", "i4"),
        ("month", "i4"),
        ("day", "i4"),
        ("hour", "i4"),
        ("MJD", float),
        ("PM_x", float),
        ("PM_y", float),
        ("UT1_UTC", float),
        ("dX_2000A", float),
        ("dY_2000A", float),
        ("PM_x_dot", float),
        ("PM_y_dot", float),
        ("LOD", float),
        ("e_PM_x", float),
        ("e_PM_y", float),
        ("e_UT1_UTC", float),
        ("e_dX_2000A", float),
        ("e_dY_2000A", float),
        ("e_PM_x_dot", float),
        ("e_PM_y_dot", float),
        ("e_LOD", float),
    ],
)
