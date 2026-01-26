from schnapsen.game import SchnapsenGamePlayEngine, Bot, PlayerPerspective, Move, GamePhase
from schnapsen.bots import RdeepBot, AlphaBetaBot, BullyBot
import random                       #for bully bot
import os                           #for adding results to csv file
import csv                          #for adding results to csv file
from statistics import mean         #for calculating averages
from typing import Optional         #for hybrit bot

engine = SchnapsenGamePlayEngine()

class BullyAlphaBeta(Bot):
    """Uses bully bot in phase one and AlphaBeta bot in phase two."""

    def __init__(self, phase_one_bot: Bot, phase_two_bot: Bot, name: str = "bully_alphabeta"):
        self._phase_one_bot = phase_one_bot
        self._phase_two_bot = phase_two_bot
        self._name = name

    def __str__(self) -> str:
        return self._name

    def get_move(
        self,
        player_perspective: PlayerPerspective,
        leader_move: Optional[Move],
    ) -> Move:
        phase = player_perspective.get_phase()
        if phase == GamePhase.TWO:
            return self._phase_two_bot.get_move(player_perspective, leader_move)
        return self._phase_one_bot.get_move(player_perspective, leader_move)

# Depth values we want to test
depths = range(1,1001)
games_per_depth = 1000
results = {}  # depth -> (rdeep_mean, alphabeta_mean, retries)

for depth in depths:
    # Create fresh bots for each depth
    rdeep_bot = RdeepBot(num_samples=12, depth=depth, rand=random.Random(), name="rdeep")
    bully_bot = BullyBot(rand=random.Random(), name="bully")
    alphabeta_bot = AlphaBetaBot(name="alphabeta")
    opponent_bot = BullyAlphaBeta(bully_bot, alphabeta_bot, name="bully_alphabeta")

    rdeep_points = []
    opponent_points = []

    # Run the tournament for this depth
    retries = 0
    games_played = 0
    while games_played < games_per_depth:
        try:
                        # Game 1: Rdeep starts
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

            # Game 2: Bully starts
            winner, _, _ = engine.play_game(opponent_bot, rdeep_bot, random.Random())
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

    print(f"Depth {depth}: Rdeep avg={rdeep_avg:.3f}, Bully+AlphaBeta avg={opponent_avg:.3f}")

output_csv = "normal_tournament_results.csv"
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