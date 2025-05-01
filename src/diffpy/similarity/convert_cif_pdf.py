from pathlib import Path

from diffpy.srreal.pdfcalculator import PDFCalculator
from diffpy.structure import Structure

Uisodefault = 0.005

typename = "Zr_O_only"
cifdir = Path(f"CIFs/{typename}")

import numpy as np
from pyobjcryst import loadCrystal

cfg = {
    "qmax": 25,
    "rmin": 0,
    "rmax": 30,
}

pc0 = PDFCalculator(**cfg)

pdfdir = Path(f"PDFs/{typename}_grs")

for ciffile in cifdir.iterdir():
    crystal = loadCrystal(ciffile)
    for sc in crystal.GetScatteringComponentList():
        sp = sc.mpScattPow
        sp.Biso = sp.Biso or 8 * np.pi**2 * Uisodefault

    r0, g0 = pc0(crystal)

    crystalcomp = None
    with open(ciffile, "r") as cifread:
        for line in cifread:
            if "_chemical_formula_structural" in line:
                crystalcomp = line.split()[1]

    with open(f"PDFs/{typename}_grs/{ciffile.stem}.cgr", "w") as grfile:
        grfile.write("i# [PDF] Computed by diffpy-cmi\n")
        grfile.write(f"composition = {crystalcomp}\n")
        grfile.write(f"qmax = {cfg['qmax']}\n")
        grfile.write(f"rmin = {cfg['rmin']}\n")
        grfile.write(f"rmax = {cfg['rmax']}\n")

        grfile.write("\n")
        grfile.write(f"# Labels: r, gr\n")
        np.savetxt(grfile, np.array([r0, g0]).T)
