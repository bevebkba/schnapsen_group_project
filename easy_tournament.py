from schnapsen.game import SchnapsenGamePlayEngine
from schnapsen.bots import RdeepBot, BullyBot #imptorting the bots that we will use
import random                       #for bully bot
import os                           #for adding results to csv file
import csv                          #for adding results to csv file
from statistics import mean         #for calculating averages

engine = SchnapsenGamePlayEngine()

# Depth values we want to test
depths = range(1,1001)
games_per_depth = 1000
results = {}  # depth -> (rdeep_mean, bully_mean, retries)

for depth in depths:
    # set the variables for the bots
    rdeep_bot = RdeepBot(num_samples=12, depth=depth, rand=random.Random(), name="rdeep")
    bully_bot = BullyBot(rand=random.Random(), name="bully")

    rdeep_points = []
    opponent_points = []

    # Run the tournament for this depth (playing two games per iteration to balance starting player)
    retries = 0
    games_played = 0

    while games_played < games_per_depth:
        try:
            # Game 1: Rdeep starts
            winner, _, _ = engine.play_game(rdeep_bot, bully_bot, random.Random())
            if str(winner) == "rdeep":
                rdeep_points.append(1)
                opponent_points.append(0)
            else:
                rdeep_points.append(0)
                opponent_points.append(1)
            games_played += 1

            if games_played >= games_per_depth:
                break

            # Game 2: Bully starts
            winner, _, _ = engine.play_game(bully_bot, rdeep_bot, random.Random())
            if str(winner) == "rdeep":
                rdeep_points.append(1)
                opponent_points.append(0)
            else:
                rdeep_points.append(0)
                opponent_points.append(1)
            games_played += 1

        except ZeroDivisionError:
            retries += 1
            continue

    rdeep_avg = mean(rdeep_points)
    opponent_avg = mean(opponent_points)
    results[depth] = (rdeep_avg, opponent_avg, retries)

    print(f"Depth {depth}: Rdeep avg={rdeep_avg:.3f}, Bully avg={opponent_avg:.3f}")

output_csv = "easy_tournament_results.csv"
file_exists = os.path.exists(output_csv)

with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # Header sadece dosya yoksa veya boşsa yazılsın
    if not file_exists or os.path.getsize(output_csv) == 0:
        writer.writerow([
            "depth",
            "rdeep_win_pct",
            "retries",
        ])

    # Add a heading row for this run
    writer.writerow([])
    writer.writerow([f"new iteration"])
    writer.writerow([
        "depth",
        "rdeep_win_pct",
        "retries",
    ])

    for depth in depths:
        rdeep_avg, opponent_avg, retries = results[depth]
        rdeep_pct = rdeep_avg * 100

        writer.writerow([
            depth,
            f"{rdeep_pct:.2f}",
            retries,
        ])

print(f"\nSaved CSV results to: {output_csv}")