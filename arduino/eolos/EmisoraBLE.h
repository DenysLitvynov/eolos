#include <cmath>
// -*- mode: c++ -*-

// --------------------------------------------------------------
//
// Autor: Jordi Bataller i Mascarell
// Editado por : Hugo Belda 
// 15/11/2025
//
// --------------------------------------------------------------

#ifndef EMISORA_H_INCLUIDO
#define EMISORA_H_INCLUIDO

// Buena introducción: https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gap
// https://os.mbed.com/blog/entry/BLE-Beacons-URIBeacon-AltBeacons-iBeacon/

// fuente: https://www.instructables.com/id/Beaconeddystone-and-Adafruit-NRF52-Advertise-Your-/
// https://github.com/nkolban/ESP32_BLE_Arduino/blob/master/src/BLEBeacon.h

// https://os.mbed.com/blog/entry/BLE-Beacons-URIBeacon-AltBeacons-iBeacon/
// https://learn.adafruit.com/bluefruit-nrf52-feather-learning-guide/bleadvertising

// ----------------------------------------------------------
// ----------------------------------------------------------
#include "ServicioEnEmisora.h"

// ----------------------------------------------------------
// ----------------------------------------------------------
class EmisoraBLE {
private:

	const char* nombreEmisora;
	const uint16_t fabricanteID;
	const int8_t txPower;

public:

	// .........................................................
	// .........................................................
	using CallbackConexionEstablecida = void(uint16_t connHandle);
	using CallbackConexionTerminada = void(uint16_t connHandle, uint8_t reason);

	// .........................................................
	// .........................................................
	EmisoraBLE(const char* nombreEmisora_, const uint16_t fabricanteID_,
	           const int8_t txPower_)
	  : nombreEmisora(nombreEmisora_),
	    fabricanteID(fabricanteID_),
	    txPower(txPower_) {
	}  // ()

	// .........................................................
	// .........................................................
	void encenderEmisora() {
		// Serial.println ( "Bluefruit.begin() " );
		Bluefruit.begin();

		// por si acaso:
		(*this).detenerAnuncio();
	}  // ()

	// .........................................................
	// .........................................................
	void encenderEmisora(CallbackConexionEstablecida cbce,
	                     CallbackConexionTerminada cbct) {

		encenderEmisora();

		instalarCallbackConexionEstablecida(cbce);
		instalarCallbackConexionTerminada(cbct);

	}  // ()

	// .........................................................
	// .........................................................
	void detenerAnuncio() {

		if ((*this).estaAnunciando()) {
			// Serial.println ( "Bluefruit.Advertising.stop() " );
			Bluefruit.Advertising.stop();
		}

	}  // ()

	// .........................................................
	// estaAnunciando() -> Boleano
	// .........................................................
	bool estaAnunciando() {
		return Bluefruit.Advertising.isRunning();
	}  // ()

	// .........................................................
	// .........................................................
	void emitirAnuncioIBeacon(uint8_t* beaconUUID, int16_t major, int16_t minor, uint8_t rssi) {

		//
		//
		//
		(*this).detenerAnuncio();

		Bluefruit.Advertising.stop();
		Bluefruit.Advertising.clearData();
		Bluefruit.ScanResponse.clearData();

		//
		// creo el beacon
		//
		BLEBeacon elBeacon(beaconUUID, major, minor, rssi);
		elBeacon.setManufacturer((*this).fabricanteID);

		//
		// parece que esto debe ponerse todo aquí
		//

		Bluefruit.setTxPower((*this).txPower);
		Bluefruit.setName((*this).nombreEmisora);
		Bluefruit.ScanResponse.addName();  // para que envíe el nombre de emisora (?!)

		//
		// pongo el beacon
		//
		Bluefruit.Advertising.setBeacon(elBeacon);

		//
		// ? qué valorers poner aquí
		//
		Bluefruit.Advertising.restartOnDisconnect(true);  // no hace falta, pero lo pongo
		Bluefruit.Advertising.setInterval(100, 100);      // in unit of 0.625 ms

		//
		// empieza el anuncio, 0 = tiempo indefinido (ya lo pararán)
		//
		Bluefruit.Advertising.start(0);

	}  // ()

	void emitirAnuncioIBeaconLibre(const char* carga, const uint8_t tamanyoCarga) {

		(*this).detenerAnuncio();

		Bluefruit.Advertising.clearData();
		Bluefruit.ScanResponse.clearData();  // hace falta?

		// Bluefruit.setTxPower( (*this).txPower ); creo que no lo pongo porque es uno de los bytes de la parte de carga que utilizo
		Bluefruit.setName((*this).nombreEmisora);
		Bluefruit.ScanResponse.addName();

		Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);

		// con este parece que no va  !
		// Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAG_LE_GENERAL_DISC_MODE);

		//
		// hasta ahora habrá, supongo, ya puestos los 5 primeros bytes. Efectivamente.
		// Falta poner 4 bytes fijos (company ID, beacon type, longitud) y 21 de carga
		//
		uint8_t restoPrefijoYCarga[4 + 21] = {
			0x4c, 0x00,  // companyID 2
			0x02,        // ibeacon type 1byte
			21,          // ibeacon length 1byte (dec=21)  longitud del resto // 0x15 // ibeacon length 1byte (dec=21)  longitud del resto
			'-', '-', '-', '-',
			'-', '-', '-', '-',
			'-', '-', '-', '-',
			'-', '-', '-', '-',
			'-', '-', '-', '-',
			'-'
		};

		//
		// addData() hay que usarlo sólo una vez. Por eso copio la carga
		// en el anterior array, donde he dejado 21 sitios libres
		//
		memcpy(&restoPrefijoYCarga[4], &carga[0], (tamanyoCarga > 21 ? 21 : tamanyoCarga));

		//
		// copio la carga para emitir
		//
		Bluefruit.Advertising.addData(BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA,
		                              &restoPrefijoYCarga[0],
		                              4 + 21);

		//
		// ? qué valores poner aquí ?
		//
		Bluefruit.Advertising.restartOnDisconnect(true);
		Bluefruit.Advertising.setInterval(100, 100);  // in unit of 0.625 ms

		Bluefruit.Advertising.setFastTimeout(1);  // number of seconds in fast mode
		//
		// empieza el anuncio, 0 = tiempo indefinido (ya lo pararán)
		//
		Bluefruit.Advertising.start(0);

		Globales::elPuerto.escribir("emitiriBeacon libre  Bluefruit.Advertising.start( 0 );  \n");
	}  // ()

	// .........................................................
	// .........................................................
	bool anyadirServicio(ServicioEnEmisora& servicio) {

		Globales::elPuerto.escribir(" Bluefruit.Advertising.addService( servicio ); \n");

		bool r = Bluefruit.Advertising.addService(servicio);

		if (!r) {
			Serial.println(" SERVICION NO AÑADIDO \n");
		}


		return r;
		// nota: uso conversión de tipo de servicio (ServicioEnEmisora) a BLEService
		// para addService()
	}  // ()


	// .........................................................
	// .........................................................
	bool anyadirServicioConSusCaracteristicas(ServicioEnEmisora& servicio) {
		return (*this).anyadirServicio(servicio);
	}  //

	// .........................................................
	template<typename... T>
	bool anyadirServicioConSusCaracteristicas(ServicioEnEmisora& servicio,
	                                          ServicioEnEmisora::Caracteristica& caracteristica,
	                                          T&... restoCaracteristicas) {

		servicio.anyadirCaracteristica(caracteristica);

		return anyadirServicioConSusCaracteristicas(servicio, restoCaracteristicas...);

	}  // ()

	// .........................................................
	template<typename... T>
	bool anyadirServicioConSusCaracteristicasYActivar(ServicioEnEmisora& servicio,
	                                                  // ServicioEnEmisora::Caracteristica & caracteristica,
	                                                  T&... restoCaracteristicas) {

		bool r = anyadirServicioConSusCaracteristicas(servicio, restoCaracteristicas...);

		servicio.activarServicio();

		return r;

	}  // ()

	// .........................................................
	// .........................................................
	void instalarCallbackConexionEstablecida(CallbackConexionEstablecida cb) {
		Bluefruit.Periph.setConnectCallback(cb);
	}  // ()

	// .........................................................
	// .........................................................
	void instalarCallbackConexionTerminada(CallbackConexionTerminada cb) {
		Bluefruit.Periph.setDisconnectCallback(cb);
	}  // ()

	// .........................................................
	// .........................................................
	BLEConnection* getConexion(uint16_t connHandle) {
		return Bluefruit.Connection(connHandle);
	}  // ()

};  // class

#endif

// ----------------------------------------------------------
// ----------------------------------------------------------
// ----------------------------------------------------------
// ----------------------------------------------------------
