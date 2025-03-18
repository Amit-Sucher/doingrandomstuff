import pandas as pd
import plotly.graph_objects as go

# Read the CSV file
df = pd.read_csv('statbotics_epa_wide.csv')

# List of team numbers to include
teams_to_include = [
    1574, 1576, 1577, 1580, 1657, 1690, 1937, 1942, 1943, 1954,
    2096, 2212, 2230, 2231, 2630, 2679, 3065, 3075, 3083, 3211,
    3316, 3339, 3388, 3835, 4319, 4320, 4338, 4416, 4586, 4590,
    4661, 4744, 5135, 5291, 5554, 5614, 5635, 5654, 5715, 5928,
    5951, 5987, 5990, 6104, 6168, 6230, 6738, 6740, 7039, 7067,
    7112, 7177, 7845, 8175, 8223, 9303, 9304, 9738, 9739, 9740,
    10139, 10695
]

# Filter DataFrame for the specified teams
df = df[df['team'].isin(teams_to_include)]

# Calculate x and y values
df['x'] = df['epa_2025_breakdown_auto_points'] + df['epa_2025_breakdown_endgame_points']
df['y'] = df['epa_2025_breakdown_teleop_points']

# Create a total metric to identify the top 5 teams
df['total'] = df['x'] + df['y']
top5 = df.sort_values('total', ascending=False).head(5)
others = df[~df.index.isin(top5.index)]

# Build the plot with Plotly Graph Objects
fig = go.Figure()

# Trace for other teams (no labels, but hover shows team and data)
fig.add_trace(go.Scatter(
    x=others['x'],
    y=others['y'],
    mode='markers',
    marker=dict(size=8, color='lightblue'),
    name='Other Teams',
    customdata=others['team'],
    hovertemplate="Team: %{customdata}<br>Auto + Endgame Points: %{x}<br>Teleop Points: %{y}<extra></extra>"
))

# Trace for top 5 teams (with labels)
fig.add_trace(go.Scatter(
    x=top5['x'],
    y=top5['y'],
    mode='markers+text',
    marker=dict(size=15, color='cyan'),
    text=top5['team'],
    customdata=top5['team'],
    textposition='top center',
    name='Top 5 Teams',
    hovertemplate="Team: %{customdata}<br>Auto + Endgame Points: %{x}<br>Teleop Points: %{y}<extra></extra>"
))

# Update layout with a sleek futuristic dark theme
fig.update_layout(
    title='Top 5 Teams EPA Graph (Futuristic) with All Teams',
    xaxis_title='Auto + Endgame Points',
    yaxis_title='Teleop Points',
    template='plotly_dark'
)

fig.show()
