from src.individual import Individual

class Hillclimber:
    """(1+1)-Hillclimber nach Roger Alsing: ein einziges Individuum, keine Population, kein Crossover.

    Pro Schritt wird eine mutierte Kopie erzeugt und nur behalten, wenn sie nicht schlechter ist.
    Hat dieselbe Schnittstelle wie `Population`, damit beide austauschbar sind.
    """

    def __init__(self, num_polygons, width, height):
        self.current = Individual(num_polygons, width, height)

    def evaluate_generation(self, renderer):
        renderer.calculate_fitness(self.current)

    def get_best_individual(self):
        return self.current

    def add_random_polygons(self, count):
        for _ in range(count):
            self.current.add_random_polygon()

    def evolve(self, renderer, evaluations):
        """Führt `evaluations` Mutationsschritte aus (je eine Fitness-Auswertung).

        So verbraucht ein Hillclimber pro "Generation" genauso viele Auswertungen
        wie der GA mit `population_size` Individuen. Der Vergleich ist damit fair.
        """
        for _ in range(evaluations):
            # mutation_rate=0.0 -> genau ein Polygon wird verändert
            child = self.current.mutate(mutation_rate=0.0)
            renderer.calculate_fitness(child)
            if child.fitness >= self.current.fitness:
                self.current = child
