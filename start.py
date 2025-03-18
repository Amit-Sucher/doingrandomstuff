from nba_api.stats.static import teams
from nba_api.stats.endpoints.teamdashboardbygeneralsplits import TeamDashboardByGeneralSplits
from nba_api.stats.endpoints.teamgamelog import TeamGameLog
import pandas as pd

def find_team(query):
    """
    Searches for a team by matching the query against the team's full name or abbreviation.
    """
    query = query.lower()
    for team in teams.get_teams():
        if query in team['full_name'].lower() or query == team['abbreviation'].lower():
            return team
    return None

def print_stat_explanations():
    """
    Prints a brief explanation for the key stats used.
    """
    explanations = {
        "NET_RATING": "Net Rating: Offensive rating minus defensive rating (points per 100 possessions). Higher is better.",
        "EFG_PCT": "Effective FG%: Adjusts for the extra value of 3-pointers—a key measure of shooting efficiency.",
        "Weighted_PM": ("Weighted Recent Plus/Minus: A composite of recent game point differentials. "
                        "The last 10 games are weighted at 60%, the next 10 at 20%, the following 10 at 10%, and the next 10 at 5%."),
    }
    print("\nStat Explanations:")
    for stat, explanation in explanations.items():
        print(f"{stat}: {explanation}")

def compute_weighted_plus_minus(team_id, season):
    """
    Computes the weighted average PLUS/MINUS (point differential) over recent games.
    Weighting is applied as follows:
      - Most recent 10 games: 60%
      - Next 10 games: 20%
      - Following 10 games: 10%
      - Next 10 games: 5%
    """
    try:
        gamelog = TeamGameLog(team_id=str(team_id), season=season)
        df = gamelog.get_data_frames()[0]
    except Exception as e:
        print(f"Error fetching game logs for team {team_id}: {e}")
        return None

    # Convert GAME_DATE to datetime (specify format if known to avoid warnings)
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE', ascending=False).reset_index(drop=True)

    weights = [0.6, 0.2, 0.1, 0.05]
    weighted_sum = 0
    total_weight = 0

    for i, weight in enumerate(weights):
        start = i * 10
        end = (i + 1) * 10
        segment = df.iloc[start:end]
        if segment.empty:
            break
        avg_pm = segment['PLUS_MINUS'].mean()
        weighted_sum += avg_pm * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else None

def main():
    # Set the season (format "YYYY-YY", e.g., "2024-25")
    season = "2024-25"

    # Get team inputs from the user
    team1_input = input("Enter team name or abbreviation for team 1: ")
    team2_input = input("Enter team name or abbreviation for team 2: ")

    team1 = find_team(team1_input)
    team2 = find_team(team2_input)
    if not team1 or not team2:
        print("One or both teams not found. Please try again.")
        return

    # Fetch advanced stats using TeamDashboardByGeneralSplits with proper lowercase parameter names
    print(f"\nFetching advanced stats for {team1['full_name']}...")
    adv_stats1 = TeamDashboardByGeneralSplits(
        team_id=str(team1['id']),
        season=season,
        measure_type="Advanced",
        per_mode="Totals",
        plus_minus="N",
        pace_adjust="N",
        rank="N"
    )
    df_adv1 = adv_stats1.get_data_frames()[0]
    print(df_adv1)

    print(f"\nFetching advanced stats for {team2['full_name']}...")
    adv_stats2 = TeamDashboardByGeneralSplits(
        team_id=str(team2['id']),
        season=season,
        measure_type="Advanced",
        per_mode="Totals",
        plus_minus="N",
        pace_adjust="N",
        rank="N"
    )
    df_adv2 = adv_stats2.get_data_frames()[0]
    print(df_adv2)

    # Extract key advanced stats
    try:
        net_rating1 = float(df_adv1['NET_RATING'].iloc[0])
        net_rating2 = float(df_adv2['NET_RATING'].iloc[0])
        efg_pct1 = float(df_adv1['EFG_PCT'].iloc[0])
        efg_pct2 = float(df_adv2['EFG_PCT'].iloc[0])
    except Exception as e:
        print("Error parsing advanced stats:", e)
        return

    # Compute weighted recent plus-minus from game logs
    weighted_pm1 = compute_weighted_plus_minus(team1['id'], season)
    weighted_pm2 = compute_weighted_plus_minus(team2['id'], season)

    print(f"\n{team1['full_name']} Advanced NET_RATING: {net_rating1}")
    print(f"{team2['full_name']} Advanced NET_RATING: {net_rating2}")
    print(f"\n{team1['full_name']} Effective FG% (EFG_PCT): {efg_pct1}")
    print(f"{team2['full_name']} Effective FG% (EFG_PCT): {efg_pct2}")

    if weighted_pm1 is not None and weighted_pm2 is not None:
        print(f"\n{team1['full_name']} Weighted Recent Plus/Minus: {weighted_pm1:.2f}")
        print(f"{team2['full_name']} Weighted Recent Plus/Minus: {weighted_pm2:.2f}")
    else:
        print("Could not compute weighted recent plus/minus for one or both teams.")

    # Composite prediction logic:
    # Award one point for a better NET_RATING and one for a better weighted PLUS/MINUS.
    score1 = 0
    score2 = 0
    if net_rating1 > net_rating2:
        score1 += 1
    elif net_rating2 > net_rating1:
        score2 += 1

    if weighted_pm1 is not None and weighted_pm2 is not None:
        if weighted_pm1 > weighted_pm2:
            score1 += 1
        elif weighted_pm2 > weighted_pm1:
            score2 += 1

    print("\nComposite Comparison:")
    print(f"{team1['full_name']} composite score: {score1}")
    print(f"{team2['full_name']} composite score: {score2}")

    if score1 > score2:
        print(f"\nPrediction: {team1['full_name']} is more likely to win based on advanced stats and recent performance.")
    elif score2 > score1:
        print(f"\nPrediction: {team2['full_name']} is more likely to win based on advanced stats and recent performance.")
    else:
        print("\nPrediction: The matchup appears very close based on the available metrics.")

    print_stat_explanations()

if __name__ == '__main__':
    main()
