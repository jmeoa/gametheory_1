from taipy.gui import Gui, notify
import pandas as pd
import numpy as np

# Variables de entrada
ley = 0.5  # %Cu
recuperacion = 0.85  # %
precio_cu = 9500  # USD/ton
tph = 1800  # Ton/hora
horas_parada = 2

# Variables adicionales
costo_hora_camion = 120  # USD/h
num_camiones = 4

# Escenarios predefinidos
def calcular_ben(estrategia):
    if estrategia == "Otra pala":
        produccion = tph * 0.7 * horas_parada  # Capacidad reducida
        ley_local = 0.45
        recup_local = 0.84
        costo = costo_hora_camion * num_camiones * horas_parada
        valor = produccion * ley_local * recup_local * precio_cu / 100
        return valor - costo

    elif estrategia == "Stockpile":
        produccion = tph * 1.0 * 1  # Solo 1 hora de stock
        costo = costo_hora_camion * num_camiones * 1
        valor = produccion * ley * recuperacion * precio_cu / 100
        return valor - costo

    elif estrategia == "Mantencion":
        ganancia_futura = 4 * costo_hora_camion  # Se evita 4h de parada futura
        costo = 0  # No se produce, pero se gana disponibilidad
        return ganancia_futura - costo

    elif estrategia == "Esperar":
        costo = costo_hora_camion * num_camiones * horas_parada
        return -costo

    return 0

estrategias = ["Otra pala", "Stockpile", "Mantencion", "Esperar"]

# Crear DataFrame de escenarios
escenarios_df = pd.DataFrame({
    "Estrategia": estrategias,
    "BEN (USD)": [calcular_ben(e) for e in estrategias]
})

# Ordenar por BEN
escenarios_df = escenarios_df.sort_values(by="BEN (USD)", ascending=False)

# Tabla de pagos para modelo tipo teoría de juegos
# Producción (fila) vs Mantención (columna)
# Valores estimados: payoff producción, payoff mantención
matriz_juego = pd.DataFrame({
    "Mantención: Solicita ventana": [(10000, 5000), (5000, 10000)],
    "Mantención: No solicita": [(15000, 0), (7000, 3000)]
}, index=["Producción: Reasigna CAEX", "Producción: Mantiene espera"])

resultado_equilibrio = "Seleccione una jugada para evaluar el equilibrio."

def evaluar_equilibrio(state):
    max_prod = 0
    mejor_jugada = ""
    for i, fila in matriz_juego.iterrows():
        for j in matriz_juego.columns:
            prod_valor, mant_valor = matriz_juego.loc[i, j]
            if prod_valor + mant_valor > max_prod:
                max_prod = prod_valor + mant_valor
                mejor_jugada = f"{i} / {j}"
    state.resultado_equilibrio = f"Equilibrio más favorable: {mejor_jugada} (Valor total combinado: {max_prod} USD)"

# Interfaz
page = """
# Simulador de Decisiones Operacionales en Minería

<|layout|columns=1 1|>
<|part|tab|label=Evaluación Económica|>

### Parámetros:
- Ley (%): <|{ley}|>
- Recuperación: <|{recuperacion}|>
- Precio Cu (USD/ton): <|{precio_cu}|>
- TPH Pala original: <|{tph}|>
- Horas parada: <|{horas_parada}|>
- Costo hora CAEX: <|{costo_hora_camion}|>
- N° Camiones: <|{num_camiones}|>

<|Recalcular|button|on_action=recalcular|>

<|Escenario comparativo (BEN en USD)|chart|type=bar|x=Estrategia|y=BEN (USD)|data=escenarios_df|>

<|Estrategias Ordenadas|table|data=escenarios_df|>

<|part|>
<|part|tab|label=Juego Estratégico|>

### Matriz de Decisión Producción vs Mantención
<|Matriz de pagos (Producción, Mantención)|table|data=matriz_juego|>

**Interpretación:**
- Fila = estrategia de Producción
- Columna = reacción de Mantención
- Cada celda muestra: (Payoff Producción, Payoff Mantención)

<|Evaluar Equilibrio|button|on_action=evaluar_equilibrio|>
<|{resultado_equilibrio}|text|>

<|part|>

|>
"""

# Callback para actualizar cálculos
def recalcular(state):
    global escenarios_df
    estrategias = ["Otra pala", "Stockpile", "Mantencion", "Esperar"]
    nuevos_ben = []
    for e in estrategias:
        tph_ = state.tph
        ley_ = state.ley
        recup_ = state.recuperacion
        precio_ = state.precio_cu
        h_parada = state.horas_parada
        n_camiones = state.num_camiones
        costo_h = state.costo_hora_camion

        if e == "Otra pala":
            prod = tph_ * 0.7 * h_parada
            valor = prod * 0.45 * 0.84 * precio_ / 100
            costo = costo_h * n_camiones * h_parada
            ben = valor - costo
        elif e == "Stockpile":
            prod = tph_ * 1.0 * 1
            valor = prod * ley_ * recup_ * precio_ / 100
            costo = costo_h * n_camiones * 1
            ben = valor - costo
        elif e == "Mantencion":
            ben = 4 * costo_h
        elif e == "Esperar":
            ben = -costo_h * n_camiones * h_parada
        nuevos_ben.append(ben)

    state.escenarios_df = pd.DataFrame({
        "Estrategia": estrategias,
        "BEN (USD)": nuevos_ben
    }).sort_values(by="BEN (USD)", ascending=False)

Gui(page).run(title="Simulador Minero - Decisión Operacional", use_reloader=True)
