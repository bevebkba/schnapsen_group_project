from schnapsen.game import SchnapsenGamePlayEngine, Bot, PlayerPerspective, Move, RegularMove, GamePhase
from schnapsen.bots import RdeepBot, BullyBot,
import random
import math
from statistics import mean
from typing import Optional
from scipy.stats import ttest_ind

engine = SchnapsenGamePlayEngine()

rdeep_bot = RdeepBot(num_samples=12, depth=5, rand=random.Random(), name="rdeep")
bully_bot = BullyBot(random.Random(), name="bullybot")

rdeep_points = []
bully_points = []

# Use a loop to run 100 games
for _ in range(100):
    # Run a game at each iteration of the loop and store the points 
    winner, game_points, _ = engine.play_game(rdeep_bot, bully_bot, random.Random())
    if str(winner) == "rdeep":
        rdeep_points.append(1)
        bully_points.append(0)
    else:
        rdeep_points.append(0)
        bully_points.append(1)

# This premade line will print the results if you completed the above code correctly
print(f"Rdeep has scored an average {mean(rdeep_points)}, while bully scored an average {mean(bully_points)}")