// -*- mode: c++ -*-

// --------------------------------------------------------------
//
// Autor: Jordi Bataller i Mascarell
// Editado por : Hugo Belda 
// 15/11/2025
//
// --------------------------------------------------------------

#ifndef MEDIDOR_H_INCLUIDO
#define MEDIDOR_H_INCLUIDO

#define PIN_GAS 28
#define PIN_VREF 29

const float SENSIBILIDAD_SENSOR = -44.75;  //Sensibilidad definida en el qr del fabricante
const int RESOLUCION_ADC = 4096;           // ADC de 12 bits
const float GAIN_TIA = 499.0;              // Ganancia del amplificador (Ω)
const float TENSION_REF_MAX = 3.3;         // Voltaje máximo ADC

// ------------------------------------------------------
// Clase Medidor
// ------------------------------------------------------
// Esta clase representa un dispositivo o módulo encargado
// de realizar mediciones de distintos tipos de sensores.
// ------------------------------------------------------
class Medidor {

  // .....................................................
  // .....................................................
private:

public:

  float voltOzono = 0.0;
  float voltRef = 0.0;
  float concentracion = 0.0;
  float concentracionFinal = 0.0;


  // .....................................................
  // constructor
  // .....................................................
  Medidor() {
  }  // ()

  void iniciarMedidor() {
    pinMode(PIN_GAS, INPUT);
    pinMode(PIN_VREF, INPUT);
  }  // ()
    // .....................................................
  // Método medirO3()
  // Mide la concentración de ozono en ppm
  // .....................................................
  float medirO3() {
    int lecturaOzono = analogRead(PIN_GAS);
    int lecturaVRef = analogRead(PIN_VREF);

    // Convertir las lecturas a voltaje real
    voltOzono = (lecturaOzono * TENSION_REF_MAX) / RESOLUCION_ADC;
    voltRef = (lecturaVRef * TENSION_REF_MAX) / RESOLUCION_ADC;

    //Calcular diferencia de voltaje
    float deltaV = voltOzono - voltRef;
    Serial.print("Lectura ADC - Vgas: ");
    Serial.print(lecturaOzono);
    Serial.print(" | Vref: ");
    Serial.println(lecturaVRef);
    Serial.print("Voltajes - Vgas: ");
    Serial.print(voltOzono, 4);
    Serial.print(" V | Vref: ");
    Serial.print(voltRef, 4);
    Serial.println(" V");

    Serial.print("Diferencia ΔV = ");
    Serial.print(deltaV * 1000, 3);
    Serial.println(" mV");

    //Calcular concentración (ppm)
    concentracion = (deltaV / (GAIN_TIA * SENSIBILIDAD_SENSOR * 1e-6));
    concentracionFinal = abs(concentracion);
    Serial.print("Concentración estimada de O3: ");
    Serial.print(concentracionFinal);
    Serial.println(" ppm");
    Serial.println("----------------------------------------");

    return concentracionFinal;
  }
  // .....................................................
  // Método medirCO2()
  // Mide la concentración de ozono en ppm
  // .....................................................
  float medirCO2() {
    return 0.04;
  }  // ()

  // .....................................................
  // Método medirTemperatura()
  // .....................................................
  // Simula la lectura de la temperatura ambiente.
  // En un caso real, leería desde un sensor como el DHT22.
  // Devuelve la temperatura como un número entero (°C).
  // .....................................................
  int medirTemperatura() {
    return -11;
  }  // ()

};  // class Medidor


// ------------------------------------------------------
// ------------------------------------------------------
// ------------------------------------------------------
// ------------------------------------------------------
#endif
