import streamlit as st
import requests
import pandas as pd
import json

API_URL = "http://worldcup26.ir:3050/get/games"

# -----------------------------
# Load rankings JSON
# -----------------------------
@st.cache_data
def load_rankings():
    with open("teams.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Map: team name -> rank points
    return {team["name"]: team["rank_points"] for team in data}


# -----------------------------
# Fetch games
# -----------------------------
@st.cache_data
def load_games():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()["games"]
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return []


# -----------------------------
# Process upsets
# -----------------------------

# -----------------------------
# Process upsets + draws
# -----------------------------
def compute_results(games, rankings):
    upsets = []
    draws = []

    for game in games:
        try:
            if game.get("finished") != "TRUE":
                continue

            home = game.get("home_team_name_en")
            away = game.get("away_team_name_en")

            home_score = int(game.get("home_score", 0))
            away_score = int(game.get("away_score", 0))

            if home not in rankings or away not in rankings:
                continue

            home_rank = rankings[home]
            away_rank = rankings[away]

            # ---------------- DRAW ----------------
            if home_score == away_score:
                draw_gap = abs(home_rank - away_rank)

                draws.append({
                    "Match": f"{home} {home_score}-{away_score} {away}",
                    "Rank": home_rank,
                    "Rank": away_rank,
                    "Rank Gap": draw_gap
                })

            # ---------------- WIN (UPSET) ----------------
            else:
                if home_score > away_score:
                    winner = home
                    loser = away
                    winner_rank = home_rank
                    loser_rank = away_rank
                else:
                    winner = away
                    loser = home
                    winner_rank = away_rank
                    loser_rank = home_rank

                upset_score = winner_rank - loser_rank

                upsets.append({
                    "Match": f"{home} {home_score}-{away_score} {away}",
                    "Winner": winner,
                    "Loser": loser,
                    "Winner Rank": winner_rank,
                    "Loser Rank": loser_rank,
                    "Upset Score": upset_score
                })

        except Exception:
            continue

    df_upsets = pd.DataFrame(upsets)
    df_draws = pd.DataFrame(draws)

    if not df_upsets.empty:
        df_upsets = df_upsets.sort_values("Upset Score")  # most negative first

    if not df_draws.empty:
        df_draws = df_draws.sort_values("Rank Gap", ascending=False)  # biggest gap first

    return df_upsets, df_draws


st.title("⚽ World Cup 2026 – Upsets & Surprising Draws")

rankings = load_rankings()
games = load_games()

df_upsets, df_draws = compute_results(games, rankings)

# ---------------- UPSSETS ----------------
st.header("🔥 Biggest Upsets")

if df_upsets.empty:
    st.info("No upsets yet.")
else:
    st.dataframe(df_upsets.head(20), use_container_width=True)

# ---------------- DRAWS ----------------
st.header("🤝 Most Surprising Draws")

if df_draws.empty:
    st.info("No draws yet.")
else:
    st.dataframe(df_draws.head(20), use_container_width=True)