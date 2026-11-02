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




Genetic Algorithm

Start (einmalig)

Das Bild wird auf working_resolution verkleinert.
Es wird eine Population aus population_size Individuen erzeugt. Jedes hat 15 zufällige Dreiecke.
Alle werden bewertet (Fitness = 1/(1+MSE)) und nach Fitness sortiert, das beste steht vorn.

Pro Generation (wiederholt max_generations mal)

Elitismus: Das beste Individuum wird unverändert in die neue Population kopiert.
Rest auffüllen, bis population_size erreicht ist. Pro Kind:
Selektion: 3 zufällige Individuen ziehen, das fitteste wird Elternteil A.
Crossover mit 70 % Wahrscheinlichkeit: ein zweites Elternteil B per Turnier wählen. Das Kind nimmt die ersten Dreiecke von A und die restlichen von B (Schnitt an zufälliger Stelle). Mit 30 % wird nur A kopiert.
Mutation: Jedes Dreieck mutiert mit 5 % Wahrscheinlichkeit (mindestens eins). Dabei wird zufällig ein Eckpunkt verschoben, die Farbe oder die Transparenz geändert.
Die neue Population ersetzt die alte.
Wachstum: Alle 5 Generationen bekommen alle Individuen 2 neue Zufallsdreiecke, bis num_polygons erreicht ist.
Bewertung: Alle Individuen werden bewertet und sortiert.
Anzeige: Alle 10 Generationen wird das beste Bild gerendert.


Hillclimber (1+1)

Gleicher Start, aber mit nur einem Individuum. Pro Generation:

population_size mal wiederholen:
Kopie des Individuums mit genau einem mutierten Dreieck erzeugen.
Bewerten.
Wenn die Kopie nicht schlechter ist, ersetzt sie das Individuum, sonst wird sie verworfen.
Wachstum und Anzeige wie beim GA.

Es gibt weder Selektion noch Crossover. Der Rest der Schleife ist identisch.

Ein Detail zum Wachstum: Die neuen Zufallsdreiecke werden nach der Reproduktion und vor der Bewertung eingefügt. Dadurch kann das beste Bild in solchen Generationen kurz schlechter werden.