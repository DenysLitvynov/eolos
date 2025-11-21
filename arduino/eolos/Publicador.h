#include <cmath>
// -*- mode: c++ -*-

// --------------------------------------------------------------
//
// Autor: Jordi Bataller i Mascarell
// Editado por : Hugo Belda 
// 15/11/2025
//
// --------------------------------------------------------------

#ifndef PUBLICADOR_H_INCLUIDO
#define PUBLICADOR_H_INCLUIDO

// --------------------------------------------------------------
// Clase que se encarga de publicar (emitir) anuncios BLE
// con diferentes tipos de mediciones (CO2, temperatura, etc.)
// utilizando la clase EmisoraBLE
// --------------------------------------------------------------
class Publicador {

	// ............................................................
	// Atributos privados
	// ............................................................
private:
	// UUID del beacon (identificador único de 16 bytes)
	uint8_t beaconUUID[16] = {
		'E', 'P', 'S', 'G', '-', 'G', 'T', 'I',
		'-', 'P', 'R', 'O', 'Y', '-', '3', 'A'
	};

	// ............................................................
	// Atributos públicos
	// ............................................................
public:
	EmisoraBLE laEmisora{
		"Grupo2PBIO",  //  nombre emisora
		0x004c,        // fabricanteID (Apple)
		4              // txPower
	};

	const int RSSI = -53;  // por poner algo, de momento no lo uso

	// ............................................................
	// ............................................................
public:

	// ............................................................
	// Enumeración para identificar los distintos tipos de mediciones
	// ............................................................
	enum MedicionesID {
		CO2 = 11,
		TEMPERATURA = 12,
		RUIDO = 13
	};

	// ............................................................
	// ............................................................
	Publicador() {
		// ATENCION: no hacerlo aquí. (*this).laEmisora.encenderEmisora();
		// Pondremos un método para llamarlo desde el setup() más tarde
	}  // ()

	// ............................................................
	// ............................................................
	void encenderEmisora() {
		(*this).laEmisora.encenderEmisora();
	}  // ()

	// ............................................................
	// Método para publicar una medición de CO2
	// ............................................................
	void publicarCO2(float_t valorCO2, uint8_t contador, long tiempoEspera) {

		// 1. Preparamos el anuncio BLE tipo iBeacon
		// 'major' codifica el tipo de medición y el número de muestra (contador)
		uint16_t major = (MedicionesID::CO2 << 8) + contador;
		int16_t minor = (int16_t)round(valorCO2 * 1000.0);  // puede ser negativo


		// Emitimos el anuncio BLE con los datos de CO2
		(*this).laEmisora.emitirAnuncioIBeacon(
		  (*this).beaconUUID,  // UUID común a todas las mediciones
		  major,               // Contiene tipo de medición + contador
		  minor,               // Valor medido (minor)
		  (*this).RSSI         // RSSI de referencia
		);


		Globales::elPuerto.escribir("   publicarCO2(): valor=");
		Globales::elPuerto.escribir(valorCO2);
		Globales::elPuerto.escribir("   contador=");
		Globales::elPuerto.escribir(contador);
		Globales::elPuerto.escribir("   todo=");
		Globales::elPuerto.escribir(major);
		Globales::elPuerto.escribir("\n");


		//
		// 2. esperamos el tiempo que nos digan
		//
		esperar(tiempoEspera);

		//
		// 3. paramos anuncio
		//
		(*this).laEmisora.detenerAnuncio();
	}  // ()

	// ............................................................
	// Método para publicar una medición de temperatura
	// ............................................................
	void publicarTemperatura(int16_t valorTemperatura, uint8_t contador, long tiempoEspera) {

		// Codificamos el tipo de medición (temperatura) junto al contador
		uint16_t major = (MedicionesID::TEMPERATURA << 8) + contador;

		// Emitimos el anuncio BLE con el valor de temperatura
		(*this).laEmisora.emitirAnuncioIBeacon(
		  (*this).beaconUUID,
		  major,
		  valorTemperatura,  // Valor medido (minor)
		  (*this).RSSI);

		// Esperamos el tiempo indicado
		esperar(tiempoEspera);

		// Detenemos la emisión del anuncio
		(*this).laEmisora.detenerAnuncio();
	}

};  // class

// --------------------------------------------------------------
// --------------------------------------------------------------
// --------------------------------------------------------------
// --------------------------------------------------------------
#endif
