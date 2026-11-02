# Hier kommt OpenCV ins Spiel. Der Renderer zeichnet aus der reinen Zahlen-Liste (DNA) ein echtes Bild
# und misst den Fehler (MSE) zum Zielbild. Das ist die schwerste Rechenaufgabe des Programms.

import numpy as np
import cv2

class Renderer:
    def __init__(self, target_image):
        """`target_image` ist das Zielbild als BGR-Array (wie von cv2 geladen)."""
        self.target_image = target_image.astype(np.float32)
        self.height, self.width = target_image.shape[:2]

    def render(self, individual):
        """Zeichnet alle Polygone der Reihe nach mit Alpha-Blending auf eine weiße Leinwand (BGR)."""
        canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        for poly in individual.polygons:
            pts = np.array([[poly[0], poly[1]], [poly[2], poly[3]], [poly[4], poly[5]]], np.int32)
            pts = pts.reshape((-1, 1, 2))
            # OpenCV-Format = BGR. Die Gene sind RGB (poly[6]=R, poly[7]=G, poly[8]=B), daher tauschen
            color = (int(poly[8]), int(poly[7]), int(poly[6]))
            alpha = poly[9] / 255.0

            # temporäre Leinwand für das Alpha-Blending
            temp_canvas = canvas.copy()
            cv2.fillPoly(temp_canvas, [pts], color)
            canvas = cv2.addWeighted(temp_canvas, alpha, canvas, 1 - alpha, 0)

        return canvas

    def calculate_fitness(self, individual):
        """Setzt und liefert die Fitness (= 1 / (1 + MSE)) gegenüber dem Zielbild.

        Je kleiner der MSE, desto ähnlicher ist das Bild dem Original und desto höher die Fitness.
        Das +1 im Nenner verhindert eine Division durch 0.
        """
        rendered_image = self.render(individual)
        mse = np.mean((self.target_image - rendered_image.astype(np.float32)) ** 2)
        individual.fitness = 1.0 / (1.0 + mse)
        return individual.fitness
