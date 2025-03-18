import statbotics
import pandas as pd

sb = statbotics.Statbotics()


def fetch_year_data(year):
    all_year_data = []
    offset = 0
    while True:
        try:
            results = sb.get_team_years(year=year, limit=100, offset=offset)
        except UserWarning:
            print(f"No more data for year {year} at offset {offset}.")
            break
        if not results:
            break
        for entry in results:
            print(f"Added team {entry.get('team')} for year {year}")
        all_year_data.extend(results)
        offset += len(results)
    return all_year_data


# Fetch data for both years
data_2024 = fetch_year_data(2024)
data_2025 = fetch_year_data(2025)

# Create DataFrames keeping only 'team' and 'epa'
df2024 = pd.DataFrame(data_2024)[['team', 'epa']]
df2025 = pd.DataFrame(data_2025)[['team', 'epa']]

# Rename the EPA column to differentiate the years
df2024.rename(columns={'epa': 'epa_2024'}, inplace=True)
df2025.rename(columns={'epa': 'epa_2025'}, inplace=True)

# Merge using 2025 as the base (teams without 2025 data are dropped)
df_combined = pd.merge(df2025, df2024, on='team', how='left')


def flatten_dict(d, parent_key='', sep='_'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            # For a list of two numbers, create low/high columns
            if len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
                items[new_key + '_low'] = v[0]
                items[new_key + '_high'] = v[1]
            else:
                items[new_key] = v
        else:
            items[new_key] = v
    return items


# Build a wide-format record per team with flattened EPA data for each year
records = []
for _, row in df_combined.iterrows():
    team = row['team']
    new_row = {'team': team}

    # Process 2025 EPA data (this must exist)
    epa_2025 = row.get('epa_2025')
    if isinstance(epa_2025, dict):
        flat_2025 = flatten_dict(epa_2025, parent_key='epa_2025')
        new_row.update(flat_2025)
    else:
        print(f"Warning: team {team} is missing 2025 EPA data.")

    # Process 2024 EPA data if available
    epa_2024 = row.get('epa_2024')
    if isinstance(epa_2024, dict):
        flat_2024 = flatten_dict(epa_2024, parent_key='epa_2024')
        new_row.update(flat_2024)

    records.append(new_row)

final_df = pd.DataFrame(records)
final_df.to_csv('statbotics_epa_wide.csv', index=False)
print("CSV created: statbotics_epa_wide.csv")
