"""Download the public Kaggle CSV used in this project and verify its identity."""
from pathlib import Path
from urllib.request import urlopen, Request
from io import BytesIO
from zipfile import ZipFile
import hashlib

ROOT=Path(__file__).resolve().parents[1]
URL='https://www.kaggle.com/api/v1/datasets/download/yashdevladdha/uber-ride-analytics-dashboard'
EXPECTED='545118f78c629cf8495770a2c16f839a5a3fbcbd0af7982c98309d5dc6db72e7'
dest=ROOT/'data/raw/ncr_ride_bookings.csv'
if dest.exists():
    raw=dest.read_bytes()
else:
    with urlopen(Request(URL,headers={'User-Agent':'Uber-Ride-Analytics-Portfolio'}),timeout=120) as r:
        archive=r.read()
    with ZipFile(BytesIO(archive)) as z:
        members=[n for n in z.namelist() if Path(n).name=='ncr_ride_bookings.csv']
        if len(members)!=1:raise RuntimeError('Expected exactly one ncr_ride_bookings.csv in the public archive.')
        raw=z.read(members[0])
actual=hashlib.sha256(raw).hexdigest()
if actual!=EXPECTED:raise RuntimeError(f'Source SHA-256 changed: {actual}. Review the dataset version before rebuilding.')
dest.parent.mkdir(parents=True,exist_ok=True)
if not dest.exists():dest.write_bytes(raw)
print(f'Verified {dest.name}: {len(raw):,} bytes; SHA-256 {actual}')
