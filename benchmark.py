"""Vergleicht GA und Hillclimber bei gleichem Budget an Fitness-Auswertungen.

Beispiel:
    python benchmark.py monalisa.png
    python benchmark.py monalisa.png --budget 30000 --seeds 3 --polygons 50 --out results

Jede Konfiguration läuft in einem eigenen Prozess. Pro Lauf werden Endfehler (MSE),
Konvergenzkurve und das Bild von Seed 0 in das Ausgabeverzeichnis geschrieben.
"""
import argparse
import json
import os
import random
import time
from multiprocessing import Pool

import cv2
import numpy as np

import src.evolution as evo
from src.evolution import run_evolution, GENETIC_ALGORITHM, HILLCLIMBER
from src.renderer import Renderer

# Schlüssel -> (Algorithmus, Populationsgröße, Mutationsrate oder None für Standard)
CONFIGS = {
    "hc":      ("Hillclimber (1+1)",        HILLCLIMBER,       30, None),
    "ga10":    ("GA, pop 10",               GENETIC_ALGORITHM, 10, None),
    "ga30":    ("GA, pop 30",               GENETIC_ALGORITHM, 30, None),
    "ga30m02": ("GA, pop 30, mut 0.02",     GENETIC_ALGORITHM, 30, 0.02),
    "ga100":   ("GA, pop 100",              GENETIC_ALGORITHM, 100, None),
}


def load_target(path, width):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"Bild nicht lesbar: {path}")
    h, w = img.shape[:2]
    return cv2.resize(img, (width, int(width * h / w)), interpolation=cv2.INTER_AREA)


def run_config(job):
    key, image, width, budget, seeds, polygons, out = job
    _, algorithm, pop, mutation_rate = CONFIGS[key]
    target = load_target(image, width)
    if mutation_rate is not None:
        evo.MUTATION_RATE = mutation_rate  # nur in diesem Prozess

    gens = budget // pop
    runs = []
    for seed in range(seeds):
        random.seed(seed)
        curve = []

        def on_progress(gen, best, renderer):
            curve.append((gen * pop, float(1 / best.fitness - 1)))

        best = run_evolution(target, algorithm, polygons, pop, gens,
                             on_progress=on_progress, progress_every=max(1, gens // 40))
        runs.append({"seed": seed, "final_mse": float(1 / best.fitness - 1), "curve": curve})
        if seed == 0:
            cv2.imwrite(os.path.join(out, f"{key}_seed0.png"), Renderer(target).render(best))

    with open(os.path.join(out, f"{key}.json"), "w") as f:
        json.dump(runs, f)
    return key, runs


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="Zielbild (JPG/PNG)")
    parser.add_argument("--budget", type=int, default=30000, help="Fitness-Auswertungen pro Lauf (Standard 30000)")
    parser.add_argument("--seeds", type=int, default=3, help="Zufalls-Seeds pro Konfiguration (Standard 3)")
    parser.add_argument("--polygons", type=int, default=50, help="Maximale Dreiecke (Standard 50)")
    parser.add_argument("--width", type=int, default=120, help="Arbeitsbreite in Pixeln (Standard 120)")
    parser.add_argument("--out", default="benchmark_results", help="Ausgabeverzeichnis")
    parser.add_argument("--configs", nargs="+", choices=list(CONFIGS), default=list(CONFIGS),
                        help="Nur diese Konfigurationen laufen lassen")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cv2.imwrite(os.path.join(args.out, "target.png"), load_target(args.image, args.width))

    jobs = [(k, args.image, args.width, args.budget, args.seeds, args.polygons, args.out) for k in args.configs]
    start = time.time()
    with Pool(len(jobs)) as pool:
        results = dict(pool.map(run_config, jobs))

    print(f"\nBudget {args.budget} Auswertungen, {args.seeds} Seeds, {args.polygons} Dreiecke "
          f"({time.time() - start:.0f}s)\n")
    print(f"{'Konfiguration':26s} {'MSE Mittel':>11s} {'min':>8s} {'max':>8s}")
    for k in args.configs:
        finals = [r["final_mse"] for r in results[k]]
        print(f"{CONFIGS[k][0]:26s} {np.mean(finals):11.1f} {min(finals):8.1f} {max(finals):8.1f}")


if __name__ == "__main__":
    main()
