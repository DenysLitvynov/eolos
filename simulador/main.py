"""
Autor: Denys Litvynov Lymanets
Fecha: 03-12-2025
Descripción: Archivo principal para ejecutar la simulación de usuarios.
"""

from simulador_usuarios import SimuladorUsuarios

if __name__ == "__main__":
    sim = SimuladorUsuarios()
    targetas = sim.leer_de_un_json("targetas.json")
    estaciones = sim.leer_de_un_json("estaciones.json")
    bicicletas = sim.leer_de_un_json("bicicletas.json")
    nums = [100, 200, 500, 1000, 2000]  # Aumentado para saturar
    results = {}
    for n in nums:
        temp = sim.obtener_temporizador_medidas(n)
        avg = sim.simular_x_numero_de_usuarios(n, estaciones, bicicletas, targetas, temp)
        results[n] = avg
        print(f"Para {n} usuarios: Latency promedio = {avg:.4f} segundos")
    sim.dibujar_grafica(results)
    print("Simulación completada. Gráfica guardada en 'grafica_latency.png'.")

