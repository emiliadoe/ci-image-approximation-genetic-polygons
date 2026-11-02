import streamlit as st
import cv2
import numpy as np
import time

from src.population import Population

# Seitenkonfiguration für ein breiteres Layout
st.set_page_config(
    page_title="PolyEvolve - Genetic Image Approximation",
    layout="wide"
)

# --- SEITENLEISTE (CONFIGURATION) ---
st.sidebar.header("Evolution Parameter")

# User Controls 
num_polygons = st.sidebar.slider("Number of Polygons (Triangles)", min_value=10, max_value=300, value=50, step=10)
population_size = st.sidebar.slider("Population Size", min_value=10, max_value=100, value=30, step=10)
max_generations = st.sidebar.slider("Number of Generations", min_value=50, max_value=2000, value=500, step=50)
working_resolution = st.sidebar.slider("Working Resolution (Pixel Width)", min_value=50, max_value=300, value=120, step=10)

st.sidebar.subheader("Genetic Operators")
mutation_rate = st.sidebar.slider("Mutation Rate (per Polygon)", min_value=0.01, max_value=0.5, value=0.05, step=0.01,
                                  help="Wahrscheinlichkeit, mit der jedes Dreieck eines Kindes mutiert wird.")
mutation_strength = st.sidebar.slider("Mutation Strength", min_value=0.5, max_value=3.0, value=1.0, step=0.25,
                                      help="Skaliert die Schrittweite (Punktverschiebung, Farbe, Transparenz).")
crossover_rate = st.sidebar.slider("Crossover Rate", min_value=0.0, max_value=1.0, value=0.7, step=0.05,
                                   help="Wahrscheinlichkeit, dass ein Kind aus zwei Eltern kombiniert wird.")
tournament_size = st.sidebar.slider("Tournament Size", min_value=2, max_value=10, value=3, step=1,
                                    help="Je größer, desto stärker der Selektionsdruck.")

st.sidebar.markdown("---")
st.sidebar.info(
    "**Tip:** A smaller working resolution (e.g., 120px) significantly accelerates the evolutionary process, "
    "as millions of pixel comparisons occur in the background."
)

st.title("Automated Vector Graphics Approximation")
st.markdown("Upload an image and watch as a genetic algorithm approximates it step by step using only polygons.")

uploaded_file = st.file_uploader("Choose an image (JPG / PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 1. Bild laden und für die Performance verkleinern
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    original_img_bgr = cv2.imdecode(file_bytes, 1)
    
    # Auf quadratische oder proportionale Arbeitsgröße skalieren
    h, w, _ = original_img_bgr.shape
    aspect_ratio = h / w
    target_h = int(working_resolution * aspect_ratio)
    original_img_bgr = cv2.resize(original_img_bgr, (working_resolution, target_h))
    
    # In RGB konvertieren für Streamlit Anzeige
    original_img_rgb = cv2.cvtColor(original_img_bgr, cv2.COLOR_BGR2RGB)

    # Layout mit zwei Spalten (Links: Original, Rechts: Evolution Live-Ansicht)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Zielbild (Original)")
        st.image(original_img_rgb, width=250)

    with col2:
        st.subheader("Vektor-Approximation (Live)")
        image_placeholder = st.empty()
        initial_canvas = np.ones((target_h, working_resolution, 3), dtype=np.uint8) * 255
        image_placeholder.image(initial_canvas, width=250)

    # Metriken-Anzeige
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    gen_metric = metric_col1.empty()
    fitness_metric = metric_col2.empty()
    status_metric = metric_col3.empty()
    
    gen_metric.metric("Current Generation", "0")
    fitness_metric.metric("Best Fitness", "-")
    status_metric.metric("Status", "Ready")

    # Start-Button für die Evolution
    if st.button("Start Evolution", type="primary"):
        status_metric.metric("Status", "Running...")
        
        # Inkrementeller Start: Wir beginnen mit wenigen Polygonen (z.B. 15) 
        # und füttern sie schrittweise bis zum ausgewählten Maximum (`num_polygons`) auf.
        current_polygons = min(15, num_polygons)
        
        pop = Population(
            size=population_size,
            num_polygons=current_polygons,
            width=working_resolution,
            height=target_h
        )
        
        # Initiale Bewertung
        pop.evaluate_generation(original_img_bgr)
        
        # Hauptschleife der Generationen
        for gen in range(1, max_generations + 1):
            pop.evolve(
                mutation_rate=mutation_rate,
                mutation_strength=mutation_strength,
                crossover_rate=crossover_rate,
                tournament_size=tournament_size,
            )

            # Alle 5 Generationen neue Dreiecke hinzufügen (bis das Maximum erreicht ist).
            # Alle Individuen wachsen gleichzeitig, damit Crossover gleich lange Genome kombiniert.
            if gen % 5 == 0 and current_polygons < num_polygons:
                add = min(2, num_polygons - current_polygons)
                current_polygons += add
                pop.add_random_polygons(add)

            pop.evaluate_generation(original_img_bgr)
            
            # UI-Update alle 10 Generationen für flüssige Live-Ansicht
            if gen % 10 == 0 or gen == max_generations:
                best_ind = pop.get_best_individual()
                
                rendered_img = best_ind.render()
                rendered_rgb = cv2.cvtColor(rendered_img, cv2.COLOR_BGR2RGB)
                
                image_placeholder.image(rendered_rgb, width=250)
                gen_metric.metric("Current Generation", str(gen))
                fitness_metric.metric("Best Fitness", f"{best_ind.fitness:.6f}")
                
        status_metric.metric("Status", "Done!")
        st.success("The evolution has been completed successfully!")

else:
    st.info("Please upload an image using the uploader on the left to get started.")