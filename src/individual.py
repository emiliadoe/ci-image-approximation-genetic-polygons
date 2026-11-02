# Chromosome/ DNA Defintion for the Genetic Algorithm
# Individuum aus einer Liste von Polygonen (Dreiecken)
# Dreieck: 3 Eckpunkte (x, y), eine Farbe und Transparenz (RGBA)

import random
import numpy as np
import cv2

class Individual:
    def __init__(self, num_polygons, width, height):
        self.width = width
        self.height = height
        self.num_polygons = num_polygons
        self.polygons = []
        self.fitness = 0.0
        
        for _ in range(self.num_polygons):
            self.add_random_polygon()

    # anfangs random generated polygon, later mutated and evolved
    def add_random_polygon(self):
        cx = random.randint(0, self.width)
        cy = random.randint(0, self.height)
        max_spread = 25  # Kompakter Radius
            
        # 3 Eckpunkte (x, y) zufällig auf der Leinwand verteilen
        x1 = max(0, min(self.width, cx + random.randint(-max_spread, max_spread)))
        y1 = max(0, min(self.height, cy + random.randint(-max_spread, max_spread)))
        x2 = max(0, min(self.width, cx + random.randint(-max_spread, max_spread)))
        y2 = max(0, min(self.height, cy + random.randint(-max_spread, max_spread)))
        x3 = max(0, min(self.width, cx + random.randint(-max_spread, max_spread)))
        y3 = max(0, min(self.height, cy + random.randint(-max_spread, max_spread)))
            
        # Zufällige Farbe (RGB) und Transparenz (Alpha)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        a = random.randint(40, 220)
            
        poly = [x1, y1, x2, y2, x3, y3, r, g, b, a]
        self.polygons.append(poly)
        self.num_polygons = len(self.polygons)

    # Kopie des Individuums: gute Individuen müssen kopiert werden, bevor wir sie mutieren
    def copy(self):
        new_ind = Individual(0, self.width, self.height)
        new_ind.width = self.width
        new_ind.height = self.height
        new_ind.num_polygons = self.num_polygons
        new_ind.polygons = [list(poly) for poly in self.polygons]
        new_ind.fitness = self.fitness
        return new_ind

# renders all polygons on a white canvas 
    def render(self):
        canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        overlay = canvas.copy()
        
        for poly in self.polygons:
            pts = np.array([
                [poly[0], poly[1]],
                [poly[2], poly[3]],
                [poly[4], poly[5]]
            ], np.int32)
            
            color = (int(poly[6]), int(poly[7]), int(poly[8]))
            alpha = poly[9] / 255.0
            
            cv2.fillPoly(overlay, [pts], color)
            canvas = cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0)
            overlay = canvas.copy()
            
        return canvas

# Fitness Value, Calculates MSE (Mean Squared Error) between the rendered image and the target image, then converts it to a fitness score.
    def evaluate(self, target_image):
        rendered_img = self.render()
        
        # MSE between gerendertem Bild und Zielbild
        mse = np.mean((target_image.astype(np.float32) - rendered_img.astype(np.float32)) ** 2)
        
        # Fitness-Formel: Je kleiner der MSE, desto höher die Fitness
        self.fitness = 1.0 / (1.0 + mse)

    def crossover(self, other):
        """One-Point-Crossover auf Polygon-Ebene: vorne Eltern A, hinten Eltern B.

        Die Reihenfolge der Polygone bestimmt die Überlagerung beim Rendern,
        daher bleibt der Schnittpunkt an derselben Position in beiden Eltern.
        """
        child = self.copy()
        n = min(len(self.polygons), len(other.polygons))
        if n < 2:
            return child

        cut = random.randint(1, n - 1)
        child.polygons = (
            [list(p) for p in self.polygons[:cut]]
            + [list(p) for p in other.polygons[cut:]]
        )
        child.num_polygons = len(child.polygons)
        child.fitness = 0.0
        return child

    def mutate(self, mutation_rate=0.03, strength=1.0):
        """Mutiert jedes Polygon mit Wahrscheinlichkeit `mutation_rate`.

        `strength` skaliert die Schrittweiten (1.0 = ±10 px, ±20 Farbe, ±15 Alpha).
        Mindestens ein Polygon wird immer mutiert, damit kein Kind identisch bleibt.
        """
        child = self.copy()
        child.fitness = 0.0

        if not child.polygons:
            return child

        indices = [i for i in range(len(child.polygons)) if random.random() < mutation_rate]
        if not indices:
            indices = [random.randint(0, len(child.polygons) - 1)]

        step_xy = max(1, int(round(10 * strength)))
        step_color = max(1, int(round(20 * strength)))
        step_alpha = max(1, int(round(15 * strength)))

        for idx in indices:
            poly = child.polygons[idx]
            mutation_choice = random.choice(['move_point', 'color', 'alpha'])

            if mutation_choice == 'move_point':
                # Verschiebe einen der drei Eckpunkte
                p_idx = random.randint(0, 2) * 2  # x0, x1 oder x2
                poly[p_idx] = max(0, min(child.width, poly[p_idx] + random.randint(-step_xy, step_xy)))
                poly[p_idx+1] = max(0, min(child.height, poly[p_idx+1] + random.randint(-step_xy, step_xy)))

            elif mutation_choice == 'color':
                # Ändere einen Farbkanal (R, G oder B)
                c_idx = random.randint(6, 8)
                poly[c_idx] = max(0, min(255, poly[c_idx] + random.randint(-step_color, step_color)))

            elif mutation_choice == 'alpha':
                # Passe die Transparenz an
                poly[9] = max(20, min(200, poly[9] + random.randint(-step_alpha, step_alpha)))

        return child