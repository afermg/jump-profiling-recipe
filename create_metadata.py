#  paths.txt produced with:
#  find ./inputs/broad -type d -name "BR*" > paths.txt
import pandas as pd

with open("paths.txt") as f:
    lines = f.read().splitlines()
batch, plates = [], []
for line in lines:
    b, p = line.split('/')[-2:]
    batch.append(b)
    plates.append(p)
meta = pd.DataFrame({"Metadata_Batch": batch, "Metadata_Plate": plates})
meta["Metadata_Source"] = "broad"
meta = meta[["Metadata_Source", "Metadata_Batch", "Metadata_Plate"]]
meta.to_csv("metadata_adipocyte.csv", index=False)