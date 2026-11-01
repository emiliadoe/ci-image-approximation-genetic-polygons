# Hier kommt OpenCV ins Spiel. Wir schreiben eine Funktion, die aus der reinen Zahlen-Liste (DNA) ein echtes Bild zeichnet und den Fehler (MSE) zum Original misst.
# Das ist die schwerste Rechenaufgabe des Programms – deshalb müssen wir das extrem effizient mit NumPy machen.

import numpy as np
import cv2

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height    
        
    def render(self, individual):
        # empty canvas
        canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        for poly in individual.polygons:
            # get the points and color
            pts = np.array([[poly[0], poly[1]], [poly[2], poly[3]], [poly[4], poly[5]]], np.int32)
            pts = pts.reshape((-1, 1, 2))
            # OpenCV format = BG. Da poly[6]=R, poly[7]=G, poly[8]=B ist muss man tauschen
            color = (int(poly[8]), int(poly[7]), int(poly[6]))
            alpha = poly[9] / 255.0  
            
            # temporary canvas for alpha blending
            temp_canvas = canvas.copy()
            cv2.fillPoly(temp_canvas, [pts], color)
            
            # Alpha-Blending: Kombiniere temp_canvas mit der Hauptleinwand
            canvas = cv2.addWeighted(temp_canvas, alpha, canvas, 1 - alpha, 0)
        
        return canvas
    
    def calculate_fitness(self, individual, target_image):
        """Berechnet die Fitness basierend auf dem Mean Squared Error (MSE)
        im Vergleich zum Original-Zielbild.
        """
        # 1. Bild des Individuums zeichnen
        rendered_image = self.render(individual)
        
        # 2. Mean Squared Error (MSE) über alle Pixel berechnen
        # Je kleiner der MSE, desto ähnlicher ist das Bild dem Original!
        mse = np.mean((target_image.astype(np.float32) - rendered_image.astype(np.float32)) ** 2)
        
        # 3. Fitness-Wert definieren: 
        # Da genetische Algorithmen meistens einen *höheren* Fitnesswert maximieren wollen,
        # kehren wir den MSE um (je kleiner der Fehler, desto höher die Fitness).
        # Wir addern +1 im Nenner, um eine Division durch 0 zu verhindern.
        fitness = 1.0 / (1.0 + mse)
        
        individual.fitness = fitness
        return fitness