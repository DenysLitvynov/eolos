
// -*- mode: c++ -*-

// --------------------------------------------------------------
//
// Autor: Jordi Bataller i Mascarell
// Editado por : Hugo Belda 
// 15/11/2025
//
// --------------------------------------------------------------

#ifndef PUERTO_SERIE_H_INCLUIDO
#define PUERTO_SERIE_H_INCLUIDO

// ----------------------------------------------------------
// Clase PuertoSerie
// Encapsula el uso del puerto serie (Serial) de Arduino para
// simplificar la inicialización y el envío de mensajes.
// ----------------------------------------------------------
class PuertoSerie  {

public:
  // .........................................................
  // Constructor: inicializa el puerto serie con la velocidad
  // de transmisión (baudios) indicada por el usuario.
  // .........................................................
  PuertoSerie (long baudios) {
	Serial.begin( baudios );
	// mejor no poner esto aquí: while ( !Serial ) delay(10);   
  } // ()

  // .........................................................
  // .........................................................
  void esperarDisponible() {

	while ( !Serial ) {
	  delay(10);   
	}

  } // ()

  // .........................................................
  // .........................................................
  template<typename T>
  void escribir (T mensaje) {
	Serial.print( mensaje );
  } // ()
  
}; // class PuertoSerie

// ----------------------------------------------------------
// ----------------------------------------------------------
// ----------------------------------------------------------
// ----------------------------------------------------------
#endif
