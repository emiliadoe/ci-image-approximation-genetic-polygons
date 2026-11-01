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

    def evolve(self):
        # 1. Elitismus: Der absolute Spitzenreiter überlebt zu 100% unberührt
        best_individual = self.individuals[0].copy()
        
        new_individuals = [best_individual]
        
        # 2. Den Rest der Population mit Mutationen des besten oder guter Eltern füllen
        while len(new_individuals) < self.size:
            # Bevorzuge den allerbesten oder Eltern aus dem oberen Viertel
            parent = self.individuals[0] if random.random() < 0.6 else random.choice(self.individuals[:int(self.size * 0.25)])
            
            child = parent.mutate()
            new_individuals.append(child)
            
        self.individuals = new_individuals