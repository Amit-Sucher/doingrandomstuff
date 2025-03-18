import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file
df = pd.read_csv('statbotics_epa_wide.csv')

# Compute x-axis as sum of auto and endgame points
df['x'] = df['epa_2025_breakdown_auto_points'] + df['epa_2025_breakdown_endgame_points']

# y-axis from teleop points
df['y'] = df['epa_2025_breakdown_teleop_points']

# Create a total metric (sum of x and y) to select the top 5 teams
df['total'] = df['x'] + df['y']

# Filter the top 5 teams based on the total metric
top5 = df.sort_values('total', ascending=False).head(5)

# Plot the data for the top 5 teams
plt.figure(figsize=(8, 6))
plt.scatter(top5['x'], top5['y'], color='blue')

# Annotate each point with its team name
for _, row in top5.iterrows():
    plt.annotate(row['team'], (row['x'], row['y']),
                 textcoords="offset points", xytext=(5, 5), ha='center')

plt.xlabel('Auto + Endgame Points')
plt.ylabel('Teleop Points')
plt.title('Top 5 Teams EPA Graph')
plt.grid(True)
plt.show()
