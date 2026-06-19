"""Train every model, then verify them all against the played WC 2026 matches.

    python3 run_all.py            # train all + verify
    python3 run_all.py --verify   # just re-run verification on existing .pkl files
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable

TRAINERS = [
    "train_logistic.py",
    "train_ordinal.py",
    "train_poisson.py",
    "train_knn.py",
    "train_naive_bayes.py",
    "train_decision_tree.py",
    "train_random_forest.py",
    "train_mlp.py",
    "train_ensemble.py",      # depends on the base models conceptually; self-contained
]


def run(script):
    print(f"\n########## {script} ##########")
    r = subprocess.run([PY, str(HERE / script)], cwd=HERE)
    if r.returncode != 0:
        print(f"!! {script} exited with {r.returncode}")
        sys.exit(r.returncode)


def main():
    if "--verify" not in sys.argv:
        for s in TRAINERS:
            run(s)
    run("verify_all.py")


if __name__ == "__main__":
    main()
