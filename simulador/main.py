"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Script principal para ejecutar pruebas de carga masiva con el simulador de usuarios.
            Genera gráfica de rendimiento del servidor.
"""

from simulador_usuarios import SimuladorUsuarios


# ---------------------------------------------------------
if __name__ == "__main__":
    """
    Ejecuta simulación de carga creciente (100 → 2000 usuarios concurrentes)
    y genera informe visual de latencia.
    """
    sim = SimuladorUsuarios()

    print("Cargando datos iniciales...")
    targetas = sim.leer_de_un_json("targetas.json")
    estaciones = sim.leer_de_un_json("estaciones.json")
    bicicletas = sim.leer_de_un_json("bicicletas.json")

    usuarios_a_probar = [100, 200, 500, 1000, 2000]
    resultados = {}

    print("Iniciando simulación de carga...\n")
    for n in usuarios_a_probar:
        print(f"Probando con {n} usuarios concurrentes...")
        temporizador = sim.obtener_temporizador_medidas(n)
        latencia_media = sim.simular_x_numero_de_usuarios(
            num_usuarios=n,
            estaciones=estaciones,
            bicicletas=bicicletas,
            targetas=targetas,
            temporizador=temporizador
        )
        resultados[n] = latencia_media
        print(f"→ {n} usuarios → Latencia media: {latencia_media:.4f} segundos\n")

    sim.dibujar_grafica(resultados)
    print("Simulación completada con éxito.")
    print("Gráfica generada: grafica_latency.png")
