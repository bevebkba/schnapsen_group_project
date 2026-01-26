from pathlib import Path
from random import Random
import csv
import time
import shutil

from schnapsen.game import SchnapsenGamePlayEngine
from schnapsen.bots import RdeepBot, MLDataBot, MLPlayingBot
from schnapsen.bots.ml_bot import train_ML_model


# -----------------
# Quick settings (simple + fast)
# -----------------
DEPTHS = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]
RDEEP_SAMPLES = 10
MODEL_ALGO = "NN"
MASTER_SEED = 1337

# Tradeoff you asked for:
TRAIN_GAMES = 1000
EVAL_GAMES = 100

# Fresh data per depth (no mixing)
FRESH_REPLAY_EACH_DEPTH = True
CLEAR_REPLAY_BEFORE_DEPTH = True

replay_dir = Path("ML_replay_memories")
models_dir = Path("ML_models")
replay_dir.mkdir(parents=True, exist_ok=True)
models_dir.mkdir(parents=True, exist_ok=True)

output_csv = "ml_tournament_data.csv"


def play_game_retry(engine: SchnapsenGamePlayEngine, bot1, bot2, rng: Random, max_retries: int = 50):
    retries = 0
    while True:
        try:
            return engine.play_game(bot1, bot2, rng), retries
        except ZeroDivisionError:
            retries += 1
            if retries >= max_retries:
                raise


def get_replay_file(iteration_id: int, depth: int) -> Path:
    if FRESH_REPLAY_EACH_DEPTH:
        folder = replay_dir / f"rdeep_replay_iter{iteration_id}_depth{depth}"
    else:
        folder = replay_dir / f"rdeep_replay_iter{iteration_id}"

    if CLEAR_REPLAY_BEFORE_DEPTH and FRESH_REPLAY_EACH_DEPTH and folder.exists():
        shutil.rmtree(folder)

    folder.mkdir(parents=True, exist_ok=True)
    return folder / "replay_memory.txt"


def next_iteration_id(csv_path: str) -> int:
    # simple: if file exists, count how many runs already logged (header excluded)
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)  # includes header
    except FileNotFoundError:
        return 0


def main() -> None:
    eng = SchnapsenGamePlayEngine()
    rng = Random(MASTER_SEED)

    file_exists = Path(output_csv).exists()
    iteration_id = next_iteration_id(output_csv)  # just a simple increasing number

    with open(output_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["iteration", "depth", "teacher_depth", "train_games", "eval_games", "ml_winrate", "seconds"])

        for depth in DEPTHS:
            t0 = time.time()

            # teacher depth = depth (stable target)
            teacher_depth = depth

            replay_file = get_replay_file(iteration_id, depth)
            model_path = models_dir / f"rdeep_model_iter{iteration_id}_depth{depth}"

            teacher = RdeepBot(RDEEP_SAMPLES, teacher_depth, Random(rng.randint(0, 2**31 - 1)))
            ml_data = MLDataBot(teacher, replay_file)

            rdeep_train = RdeepBot(RDEEP_SAMPLES, depth, Random(rng.randint(0, 2**31 - 1)))

            # 1) collect training data
            for _ in range(TRAIN_GAMES):
                if rng.random() < 0.5:
                    play_game_retry(eng, ml_data, rdeep_train, rng)
                else:
                    play_game_retry(eng, rdeep_train, ml_data, rng)

            # 2) train model
            train_ML_model(replay_file, model_path, MODEL_ALGO)

            # 3) evaluate
            ml_player = MLPlayingBot(model_path)
            rdeep_eval = RdeepBot(RDEEP_SAMPLES, depth, Random(rng.randint(0, 2**31 - 1)))

            ml_wins = 0
            for _ in range(EVAL_GAMES):
                if rng.random() < 0.5:
                    (winner, _, _), _ = play_game_retry(eng, ml_player, rdeep_eval, rng)
                else:
                    (winner, _, _), _ = play_game_retry(eng, rdeep_eval, ml_player, rng)
                if winner == ml_player:
                    ml_wins += 1

            winrate = ml_wins / EVAL_GAMES
            elapsed = time.time() - t0

            writer.writerow([iteration_id, depth, teacher_depth, TRAIN_GAMES, EVAL_GAMES, f"{winrate:.4f}", f"{elapsed:.1f}"])
            f.flush()

            print(f"[iter {iteration_id}] depth={depth} winrate={winrate:.3f} ({winrate*100:.1f}%) time={elapsed:.1f}s")


if __name__ == "__main__":
    main()