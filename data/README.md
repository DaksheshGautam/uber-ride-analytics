# Dataset

Source: [Yashdev Laddha, Uber Ride Analytics Dashboard on Kaggle](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard).

Run `python scripts/download_data.py`, or place `ncr_ride_bookings.csv` under `data/raw/` manually. The raw file should contain 150,000 rows and 21 columns.

Expected SHA-256: `545118f78c629cf8495770a2c16f839a5a3fbcbd0af7982c98309d5dc6db72e7`.

Raw/cleaned CSVs and the generated SQLite database are not committed. The PBIX contains an embedded snapshot for review. `scripts/analyze.py` rebuilds the cleaned fact, dimensions, calendar, database, query results and validation outputs.

Source data rights remain with their respective owners. This repository does not relicense the Kaggle dataset. Sampling, provenance, currency, distance and timing units are unverified.
