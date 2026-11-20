import hashlib
import json
from datetime import datetime, timezone
from urllib.request import urlopen

from data_preparation import ROOT, FILES

directory = ROOT / 'data'
directory.mkdir(exist_ok=True)
base = 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/'
records = []
for stem in FILES:
    name = f'{stem}.xpt'
    path = directory / name
    if not path.exists():
        with urlopen(base + name, timeout=120) as response:
            content = response.read()
        if not content.startswith(b'HEADER RECORD'):
            raise ValueError(f'{name}: server did not return a SAS transport file')
        path.write_bytes(content)
        status = 'downloaded'
    else:
        content = path.read_bytes()
        if not content.startswith(b'HEADER RECORD'):
            raise ValueError(f'{path}: invalid SAS transport file')
        status = 'reused local file'
    records.append({'file': name, 'url': base + name, 'status': status, 'checked_utc': datetime.now(timezone.utc).isoformat(), 'sha256': hashlib.sha256(content).hexdigest()})
    print(name, status)
(directory / 'retrieval.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
