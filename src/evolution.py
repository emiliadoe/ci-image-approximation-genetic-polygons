from src.population import Population
from src.hillclimber import Hillclimber
from src.renderer import Renderer

GENETIC_ALGORITHM = "Genetic Algorithm"
HILLCLIMBER = "Hillclimber (1+1)"

# Feste GA-Parameter (nicht in der UI einstellbar)
MUTATION_RATE = 0.05      # Wahrscheinlichkeit pro Dreieck, mutiert zu werden
MUTATION_STRENGTH = 1.0   # Skaliert die Schrittweite der Mutation
CROSSOVER_RATE = 0.7      # Wahrscheinlichkeit, dass ein Kind aus zwei Eltern entsteht
TOURNAMENT_SIZE = 3       # Anzahl Kandidaten pro Eltern-Turnier

# Inkrementeller Start: wenige Polygone, die schrittweise bis zum Maximum aufgefüttert werden
START_POLYGONS = 15
GROWTH_EVERY = 5          # alle n Generationen ...
GROWTH_STEP = 2           # ... kommen so viele Dreiecke dazu


def run_evolution(target_bgr, algorithm, num_polygons, population_size, max_generations,
                  on_progress=None, progress_every=10):
    """Führt die Evolution aus und gibt das beste Individuum zurück.

    `target_bgr` ist das Zielbild (BGR, bereits auf Arbeitsgröße skaliert).
    `on_progress(gen, best_individual, renderer)` wird alle `progress_every` Generationen
    und nach der letzten Generation aufgerufen, z.B. für eine Live-Anzeige.
    """
    renderer = Renderer(target_bgr)
    current_polygons = min(START_POLYGONS, num_polygons)
    use_ga = algorithm == GENETIC_ALGORITHM

    if use_ga:
        pop = Population(population_size, current_polygons, renderer.width, renderer.height)
    else:
        pop = Hillclimber(current_polygons, renderer.width, renderer.height)

    pop.evaluate_generation(renderer)

    for gen in range(1, max_generations + 1):
        if use_ga:
            pop.evolve(
                mutation_rate=MUTATION_RATE,
                mutation_strength=MUTATION_STRENGTH,
                crossover_rate=CROSSOVER_RATE,
                tournament_size=TOURNAMENT_SIZE,
            )
        else:
            # Gleiches Auswertungsbudget wie eine GA-Generation
            pop.evolve(renderer, population_size)

        # Neue Dreiecke hinzufügen (bis das Maximum erreicht ist).
        # Alle Individuen wachsen gleichzeitig, damit Crossover gleich lange Genome kombiniert.
        if gen % GROWTH_EVERY == 0 and current_polygons < num_polygons:
            add = min(GROWTH_STEP, num_polygons - current_polygons)
            current_polygons += add
            pop.add_random_polygons(add)

        pop.evaluate_generation(renderer)

        if on_progress and (gen % progress_every == 0 or gen == max_generations):
            on_progress(gen, pop.get_best_individual(), renderer)

    return pop.get_best_individual()
