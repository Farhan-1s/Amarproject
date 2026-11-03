# Raw Data: NHANES 2021–2023

Due to size constraints and version control best practices, raw data files (`*.XPT`) are excluded from this repository via `.gitignore`. 

## Automated Download
To populate this directory with the exact files required for the analysis, run the provided script from the project root:

```bash
python -c '
import os, urllib.request
os.makedirs("data", exist_ok=True)
files = ["DEMO_L.xpt", "BMX_L.xpt", "TCHOL_L.xpt", "HDL_L.xpt", "BPQ_L.xpt", "SMQ_L.xpt"]
url = "[https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/)"
for f in files: urllib.request.urlretrieve(url+f, f"data/{f}")
'