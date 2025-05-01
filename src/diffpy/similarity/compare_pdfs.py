from pathlib import Path

import numpy as np

from diffpy.pdfmorph.pdfmorphpy import pdfmorph
from diffpy.utils.parsers import loadData

grnames = [
    "Si_O_only_10_common_grs",
    "Ti_O_only_10_common_grs",
    "Zr_O_only_10_common_grs",
]

gr_list = []

for grname in grnames:
    grdir = Path(f"PDFs/{grname}")

    gr_list_component = list(grdir.iterdir())
    gr_list_component.sort()

    gr_list.extend(gr_list_component)

grname = "All_O_only_10_common_grs"

datmatrw = []
datmatrw_morph = []

datmatpcc = []
datmatpcc_morph = []

labels = []

for grfile1 in gr_list:
    with open(grfile1, "r") as grread:
        for line in grread:
            if "composition =" in line:
                labels.append(line.split("=")[1].strip())

    datrw_row = []
    datpcc_row = []

    datrw_row_morph = []
    datpcc_row_morph = []

    for grfile2 in gr_list:
        rawdata = pdfmorph(grfile1, grfile2, noplot="")[0]
        morphdata = pdfmorph(grfile1, grfile2, noplot="", stretch=0, scale=1)[
            0
        ]

        datrw_row.append(rawdata["Rw"])
        datpcc_row.append(rawdata["Pearson"])

        datrw_row_morph.append(morphdata["Rw"])
        datpcc_row_morph.append(morphdata["Pearson"])

    datmatrw.append(datrw_row)
    datmatrw_morph.append(datrw_row_morph)

    datmatpcc.append(datpcc_row)
    datmatpcc_morph.append(datpcc_row_morph)

datmatrw = np.array(datmatrw)
datmatrw = np.sqrt(datmatrw * datmatrw.T)

datmatrw_morph = np.array(datmatrw_morph)
datmatrw_morph = np.sqrt(datmatrw_morph * datmatrw_morph.T)

datmatpcc = np.array(datmatpcc)
datmatpcc = (1 - datmatpcc) / 2
datmatpcc_morph = np.array(datmatpcc_morph)
datmatpcc_morph = (1 - datmatpcc_morph) / 2

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

for idx, df in enumerate(
    [datmatrw, datmatrw_morph, datmatpcc, datmatpcc_morph]
):
    dm = pd.DataFrame(df, index=labels, columns=labels)

    mask = np.triu(
        np.ones_like(np.array(dm), dtype=bool)
    )  # make a lower triangular mask
    # Plot the heatmap with the mask
    plt.figure(figsize=(15, 12))
    sns.heatmap(dm, annot=False, vmin=0, vmax=1)
    plt.grid(False)
    plt.tight_layout()

    iname = None
    if idx == 0:
        iname = "Rw"
    elif idx == 1:
        iname = "Rw-morphed"
    elif idx == 2:
        iname = "Pcc"
    elif idx == 3:
        iname = "Pcc-morphed"
    dm.to_csv(Path("figs/CSVs") / f"{grname}-{iname}.csv")
    plt.savefig(Path("figs") / f"{grname}-{iname}.png", dpi=300)
    plt.savefig(Path("figs") / f"{grname}-{iname}.svg", dpi=300)

    plt.show()
