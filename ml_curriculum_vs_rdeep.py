from pathlib import Path
from random import Random
import os, csv

from schnapsen.game import SchnapsenGamePlayEngine
from schnapsen.bots import RdeepBot, MLDataBot, MLPlayingBot
from schnapsen.bots.ml_bot import train_ML_model


# -----------------
# Settings
# -----------------
TRAIN_GAMES_PER_ITER = 1000
EVAL_GAMES_PER_ITER = 1000
START_DEPTH = 1
DEPTHS = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]
MAX_DEPTH = 10            # kaç iterasyon/depth deneyeceksiniz
RDEEP_SAMPLES = 10        # RdeepBot num_samples
TEACHER_NAME = "rdeep"
TEACHER_DEPTH = 10        # Teacher Rdeep depth (should be >= current opponent depth)
MODEL_ALGO = "LR"

replay_dir = Path("ML_replay_memories")
models_dir = Path("ML_models")
replay_dir.mkdir(parents=True, exist_ok=True)
models_dir.mkdir(parents=True, exist_ok=True)

output_csv = "ml_tournament_data.csv"


def next_iteration_id(csv_path: str) -> int:
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return 1
    max_seen = 0
    with open(csv_path, "r", encoding="utf-8") as rf:
        for line in rf:
            line = line.strip().lower()
            if line.startswith("iteration "):
                parts = line.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    max_seen = max(max_seen, int(parts[1]))
    return max_seen + 1 if max_seen > 0 else 1


def play_game_retry(engine: SchnapsenGamePlayEngine, bot1, bot2, rng: Random, max_retries: int = 50):
    """Play a game, retrying if a bot crashes due to known RdeepBot ZeroDivisionError (0/0 heuristic)."""
    retries = 0
    while True:
        try:
            return engine.play_game(bot1, bot2, rng), retries
        except ZeroDivisionError:
            retries += 1
            if retries >= max_retries:
                raise


eng = SchnapsenGamePlayEngine()
rng = Random()

iteration_id = next_iteration_id(output_csv)

with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    # İlk defa oluşturuluyorsa genel başlık
    if os.path.getsize(output_csv) == 0:
        writer.writerow(["note", "This CSV appends runs. Each iteration block contains: depth, train_games, eval_games, ml_winrate"])

    for depth in DEPTHS:
        # -----------------
        # 1) Collect data vs current Rdeep depth
        # -----------------
        replay_path = replay_dir / f"{TEACHER_NAME}_replay_iter{iteration_id}"  # accumulate across depths in this run
        model_path = models_dir / f"{TEACHER_NAME}_model_iter{iteration_id}_depth{depth}"

        # Teacher should be at least as strong as the current opponent depth
        teacher_depth = max(TEACHER_DEPTH, depth)
        teacher = RdeepBot(RDEEP_SAMPLES, teacher_depth, Random())

        # MLDataBot: teacher'ın kararlarını replay'e yazar
        ml_data = MLDataBot(teacher, replay_path)

        rdeep_train = RdeepBot(RDEEP_SAMPLES, depth, Random())

        train_retries = 0
        games_done = 0
        while games_done < TRAIN_GAMES_PER_ITER:
            if rng.random() < 0.5:
                (_, _, _), retries = play_game_retry(eng, ml_data, rdeep_train, rng)
            else:
                (_, _, _), retries = play_game_retry(eng, rdeep_train, ml_data, rng)
            train_retries += retries
            games_done += 1

        # -----------------
        # 2) Train model from replay
        # -----------------
        train_ML_model(
            replay_path,
            model_path,
            MODEL_ALGO
        )

        # -----------------
        # 3) Evaluate MLPlayingBot vs same depth Rdeep
        # -----------------
        ml_player = MLPlayingBot(model_path)
        rdeep_eval = RdeepBot(RDEEP_SAMPLES, depth, Random())

        eval_retries = 0
        ml_wins = 0
        games_done = 0

        while games_done < EVAL_GAMES_PER_ITER:
            if rng.random() < 0.5:
                (winner, _, _), retries = play_game_retry(eng, ml_player, rdeep_eval, rng)
            else:
                (winner, _, _), retries = play_game_retry(eng, rdeep_eval, ml_player, rng)
            eval_retries += retries
            if winner == ml_player:
                ml_wins += 1
            games_done += 1

        ml_winrate = ml_wins / EVAL_GAMES_PER_ITER

        # -----------------
        # 4) Log block
        # -----------------
        writer.writerow([])
        writer.writerow([f"iteration {iteration_id} (depth {depth})"])
        writer.writerow(["depth", "train_games", "eval_games", "ml_winrate"])
        writer.writerow([depth, TRAIN_GAMES_PER_ITER, EVAL_GAMES_PER_ITER, f"{ml_winrate:.4f}"])

        print(f"[iter {iteration_id}] depth={depth}  ML winrate vs Rdeep = {ml_winrate:.3f}")

print(f"\nSaved curriculum results to: {output_csv}")