# Lebanon Public Transport and Road Infrastructure (2023)

Streamlit app built for **MSBA 325 - Interactive Visualizations with Streamlit**, American University of Beirut.

**Live app:** PASTE_YOUR_STREAMLIT_LINK_HERE

## What it does

The app explores town-level survey data on public transport and road conditions in Lebanon. It shows:

- the share of towns with dedicated bus stops, by area
- the reported condition of main roads, by area
- headline numbers for the current selection

## The two linked interaction features

1. **Governorate dropdown** sets the frame of reference for the whole page.
2. **District multiselect** whose options are rebuilt from the governorate chosen above, so the reader drills down instead of filtering two things independently.

## Data

Public Transportation - Lebanon 2023 (Impact Open Data), published through the AUB PKGCubes Explorer, Social Data domain. The file `Public_Transportation_Lebanon_2023.csv` in this repository is the copy used by the app.

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Author: Christian Ghassibe
