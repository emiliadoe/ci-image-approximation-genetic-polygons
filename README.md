# ci-image-approximation-genetic-polygons
Converting a raster image (bitmap/JPG) into a scalable vector format (consisting of mathematical polygons)



Der Hillclimber ist als zweite Option eingebaut, und in meinem Test schlägt er den GA deutlich. Die Streamlit-UI habe ich dabei nicht gestartet.

Was neu ist
hillclimber.py: Ein (1+1)-Hillclimber wie bei Alsing. Er hat ein einziges Individuum und pro Schritt eine mutierte Kopie mit genau einem veränderten Dreieck. Die Kopie wird nur behalten, wenn sie nicht schlechter ist.
app.py: In der Sidebar gibt es eine Auswahl Algorithm mit „Genetic Algorithm“ und „Hillclimber (1+1)“. Alles andere (Dreiecke, Wachstum, Live-Ansicht) bleibt gleich.
Fairer Vergleich: Der Hillclimber macht pro „Generation“ genauso viele Mutationsschritte, wie der GA Individuen hat (population_size). Beide verbrauchen also gleich viele Fitness-Auswertungen, und die Laufzeit ist vergleichbar.
Testergebnis

Test mit 5 Seeds, 200 Generationen, Population 30 und einem kleinen synthetischen Bild. Gemessen wird der MSE (kleiner ist besser):

	MSE je Seed	Mittel
Genetic Algorithm	2710, 3515, 2967, 3063, 3813	3214
Hillclimber	1778, 2190, 1259, 1964, 1863	1811

Der Hillclimber ist bei jedem Seed besser, im Schnitt um etwa 44 %. Ich hatte oben schon vermutet, dass bei so glatten Problemen Hillclimber oft besser abschneiden als GAs. Das bestätigt sich hier.

Warum der GA zurückliegt

Vermutlich liegt es an den Parametern. Der GA verändert pro Kind etwa 2–3 Dreiecke gleichzeitig, der Hillclimber nur eines. Bei gleichem Budget kann der Hillclimber jede Änderung einzeln prüfen, beim GA wird eine gute Änderung oft von einer schlechten im selben Kind überdeckt. Eine Mutation Rate von etwa 0.02 würde den GA näher an den Hillclimber bringen. Das habe ich nicht getestet.

Für deine Dokumentation wäre das ein ehrliches Ergebnis: Der GA bringt auf diesem Problem keinen Vorteil gegenüber Alsings Verfahren. Ein Test mit einem echten Foto steht noch aus. Soll ich dafür die GA-Parameter durchprobieren und schauen, ob sich das Bild dreht?