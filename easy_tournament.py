from schnapsen.game import SchnapsenGamePlayEngine
from schnapsen.bots import RdeepBot, BullyBot # Import the bots we need
import random                       # needed for bot decisions and game shuffling.
import os                           # to check if the csv file already exists.
import csv                          # to save tournament results to a csv file for later analysis.
from statistics import mean         # for calculating win rates.

# name the engine
engine = SchnapsenGamePlayEngine()

# make a variable to 
depths = range(1,1001)
# we used 1000 games per depth to get a reliable average.
games_per_depth = 1000

# The file where we will store the win rates.
output_csv = "easy_tournament_results.csv"
file_exists = os.path.exists(output_csv)

# Prepare the CSV file. If it's new, we add headers. If it exists, we add a separator.
with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists or os.path.getsize(output_csv) == 0:
        writer.writerow(["depth", "rdeep_win_pct", "retries"])
    else:
        # If file exists, add a separator and new headers for a new run
        writer.writerow([]), writer.writerow(["new iteration"]), writer.writerow(["depth", "rdeep_win_pct", "retries"])

# Iterate through all the depths we want to test.
for depth in depths:
    # Initialize the bots.
    # Our hero: RdeepBot, configured with the current depth being tested.
    rdeep_bot = RdeepBot(num_samples=12, depth=depth, rand=random.Random(), name="rdeep")
    # The challenger: BullyBot, a simple deterministic bot.
    bully_bot = BullyBot(rand=random.Random(), name="bully")

    rdeep_points = []
    opponent_points = []

    # we set the 
    retries = 0
    games_played = 0

    while games_played < games_per_depth:
        try:
            # First game of the pair: RdeepBot takes the lead.
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

            # Second game of the pair: BullyBot takes the lead to ensure fairness.
            winner, _, _ = engine.play_game(bully_bot, rdeep_bot, random.Random())
            if str(winner) == "rdeep":
                rdeep_points.append(1)
                opponent_points.append(0)
            else:
                rdeep_points.append(0)
                opponent_points.append(1)
            games_played += 1

        except ZeroDivisionError:
            # to prevent Zero Division Error
            retries += 1
            continue

    # calculate the win rate at each depth.
    rdeep_avg = mean(rdeep_points)
    opponent_avg = mean(opponent_points)

    # show us the progress in the terminal.
    print(f"Depth {depth}: Rdeep avg={rdeep_avg:.3f}, Bully avg={opponent_avg:.3f}")
    # save the data right away so we don't lose progress if the script stops.
    with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([depth, f"{rdeep_avg * 100:.2f}", retries])