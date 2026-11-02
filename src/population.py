import random
from src.individual import Individual

class Population:
    def __init__(self, size, num_polygons, width, height):
        self.size = size
        self.num_polygons = num_polygons
        self.width = width
        self.height = height
        
        # Erstelle die Population aus Individuen
        self.individuals = [
            Individual(num_polygons, width, height) 
            for _ in range(size)
        ]

    def evaluate_generation(self, target_image):
        """Bewertet alle Individuen der Population gegen das Zielbild."""
        for ind in self.individuals:
            ind.evaluate(target_image)
            
        # Sortiere absteigend nach Fitness (höchste Fitness zuerst)
        self.individuals.sort(key=lambda x: x.fitness, reverse=True)

    def get_best_individual(self):
        """Gibt das aktuell beste Individuum (mit der höchsten Fitness) zurück."""
        # Da nach evaluate_generation sortiert wurde, ist das erste Element das beste
        return self.individuals[0]

    def add_random_polygons(self, count):
        """Fügt jedem Individuum `count` neue Polygone hinzu (Population bleibt gleich lang)."""
        for ind in self.individuals:
            for _ in range(count):
                ind.add_random_polygon()

    def _tournament_select(self, tournament_size):
        """Zieht `tournament_size` zufällige Individuen und gibt das fitteste zurück."""
        k = max(1, min(tournament_size, len(self.individuals)))
        return max(random.sample(self.individuals, k), key=lambda x: x.fitness)

    def evolve(self, mutation_rate=0.03, mutation_strength=1.0,
               crossover_rate=0.7, tournament_size=3, elite_count=1):
        # 1. Elitismus: die besten Individuen überleben unverändert
        new_individuals = [ind.copy() for ind in self.individuals[:elite_count]]

        # 2. Rest per Turnier-Selektion, Crossover und Mutation auffüllen
        while len(new_individuals) < self.size:
            parent_a = self._tournament_select(tournament_size)

            if random.random() < crossover_rate:
                parent_b = self._tournament_select(tournament_size)
                child = parent_a.crossover(parent_b)
            else:
                child = parent_a.copy()

            child = child.mutate(mutation_rate, mutation_strength)
            new_individuals.append(child)

        self.individuals = new_individuals