from schnapsen.game import SchnapsenGamePlayEngine, Bot, PlayerPerspective, Move, RegularMove, GamePhase
from schnapsen.bots import RdeepBot, BullyBot
import random
import math
import csv
from statistics import mean
from typing import Optional
from scipy.stats import ttest_ind

engine = SchnapsenGamePlayEngine()

# Depth values we want to test
depths = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]

games_per_depth = 1000
results = {}  # depth -> (rdeep_mean, bully_mean, retries)

for depth in depths:
    # Create fresh bots for each depth
    rdeep_bot = RdeepBot(num_samples=12, depth=depth, rand=random.Random(), name="rdeep")
    bully_bot = BullyBot(random.Random(), name="bullybot")

    rdeep_points = []
    bully_points = []

    # Run the tournament for this depth
    retries = 0
    games_played = 0
    while games_played < games_per_depth:
        try:
            winner, game_points, _ = engine.play_game(rdeep_bot, bully_bot, random.Random())
        except ZeroDivisionError:
            retries += 1
            continue
        if str(winner) == "rdeep":
            rdeep_points.append(1)
            bully_points.append(0)
        else:
            rdeep_points.append(0)
            bully_points.append(1)
        games_played += 1

    rdeep_avg = mean(rdeep_points)
    bully_avg = mean(bully_points)
    results[depth] = (rdeep_avg, bully_avg, retries)

    print(f"Depth {depth}: Rdeep avg={rdeep_avg:.3f}, Bully avg={bully_avg:.3f}")

# Write results to a CSV file in the same directory as this script
output_csv = "tournament_results.csv"
with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "depth",
        "games_per_depth",
        "rdeep_avg",
        "bully_avg",
        "rdeep_win_pct",
        "bully_win_pct",
        "retries",
    ])

    for depth in depths:
        rdeep_avg, bully_avg, retries = results[depth]
        rdeep_pct = rdeep_avg * 100
        bully_pct = bully_avg * 100

        writer.writerow([
            depth,
            games_per_depth,
            f"{rdeep_avg:.6f}",
            f"{bully_avg:.6f}",
            f"{rdeep_pct:.2f}",
            f"{bully_pct:.2f}",
            retries,
        ])

print(f"\nSaved CSV results to: {output_csv}")