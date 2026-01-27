# This script evaluates the performance of an R-deep agent with increasing search depth against a medium-strength hybrid opponent composed of Bully and AlphaBeta bots. It runs multiple games per depth setting, records win-rate statistics, and logs the results to a CSV file to analyze win-rate variance as depth increases.

from schnapsen.game import SchnapsenGamePlayEngine, Bot, PlayerPerspective, Move, GamePhase  # Core game engine and abstractions
from schnapsen.bots import RdeepBot, AlphaBetaBot, BullyBot # Importing the bots that we will use
import random                       # For randomness in bots and game play
import os                           # For checking and handling CSV file existence
import csv                          # For logging results to CSV file
from statistics import mean         # For calculating average win rates
from typing import Optional         # For type hinting in hybrid bot

engine = SchnapsenGamePlayEngine()

# Hybrid opponent used as the medium-strength baseline: combines BullyBot in phase one and AlphaBetaBot in phase two
class BullyAlphaBeta(Bot):
    """Uses bully bot in phase one and AlphaBeta bot in phase two."""

    def __init__(self, phase_one_bot: Bot, phase_two_bot: Bot, name: str = "bully_alphabeta"):
        """Initialize hybrid bot with two separate bots for different game phases."""
        self._phase_one_bot = phase_one_bot
        self._phase_two_bot = phase_two_bot
        self._name = name

    def __str__(self) -> str:
        return self._name

    # Selects move based on current phase: phase one uses bully bot, phase two uses alphabeta bot
    def get_move(
        self,
        player_perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        phase = player_perspective.get_phase()
        if phase == GamePhase.TWO:
            return self._phase_two_bot.get_move(player_perspective, leader_move)
        return self._phase_one_bot.get_move(player_perspective, leader_move)

# Experimental design parameters:
# Sweep over depths from 1 to 1000, playing a fixed number of games per depth to evaluate performance
depths = range(1,1001)
games_per_depth = 1000
results = {}  # depth -> (rdeep_mean, alphabeta_mean, retries)

for depth in depths:
    # Instantiate bots for the current depth setting
    rdeep_bot = RdeepBot(num_samples=12, depth=depth, rand=random.Random(), name="rdeep")
    bully_bot = BullyBot(rand=random.Random(), name="bully")
    alphabeta_bot = AlphaBetaBot(name="alphabeta")
    opponent_bot = BullyAlphaBeta(bully_bot, alphabeta_bot, name="bully_alphabeta")

    # Lists to record binary outcomes (1 for win, 0 for loss) for each bot
    rdeep_points = []
    opponent_points = []

    # Play two games per iteration to balance the advantage of starting first between bots
    retries = 0
    games_played = 0
    while games_played < games_per_depth:
        try:
            # Game 1: Rdeep starts first to evaluate its performance when leading
            winner, _, _ = engine.play_game(rdeep_bot, opponent_bot, random.Random())
            if str(winner) == "rdeep":
                rdeep_points.append(1)
                opponent_points.append(0)
            else:
                rdeep_points.append(0)
                opponent_points.append(1)
            games_played += 1

            if games_played >= games_per_depth:
                break

            # Game 2: Opponent (bully_alphabeta) starts first to balance starting advantage
            winner, _, _ = engine.play_game(opponent_bot, rdeep_bot, random.Random())
            if str(winner) == "rdeep":
                rdeep_points.append(1)
                opponent_points.append(0)
            else:
                rdeep_points.append(0)
                opponent_points.append(1)
            games_played += 1

        except ZeroDivisionError:
            # Count retries when ZeroDivisionError occurs due to rare edge cases in game logic
            # This ensures reliable statistics by replaying problematic games
            retries += 1
            continue
    # Compute win rate as the mean of binary win/loss outcomes for Rdeep and opponent
    rdeep_avg = mean(rdeep_points)
    opponent_avg = mean(opponent_points)
    results[depth] = (rdeep_avg, opponent_avg, retries)

    print(f"Depth {depth}: Rdeep avg={rdeep_avg:.3f}, Bully+AlphaBeta avg={opponent_avg:.3f}")

output_csv = "normal_tournament_results.csv"
file_exists = os.path.exists(output_csv)

# Logging strategy: append results to CSV, write header only if file is new or empty,
# and add separation rows between iterations for clarity
with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # Write header if file is new or empty
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

# Confirm successful storage of results to CSV
print(f"\nSaved CSV results to: {output_csv}")