// MetradoModel.kt
package com.example.metradosapp.model

data class ProyectoMetrado(
    val nombreProyecto: String,
    val ubicacion: String,
    val metrados: List<PartidaMetrado>
)

data class PartidaMetrado(
    val id: String = java.util.UUID.randomUUID().toString(),
    val codigoOE: String,      // Ej: OE.2.3.1
    val descripcion: String,   // Ej: ZAPATAS - CONCRETO 210 kg/cm2
    val unidad: String,        // Ej: m3, m2, kg, pza
    val detalles: List<DetalleCalculo>
) {
    // Total acumulado de la partida
    val total: Double get() = detalles.sumOf { it.parcial }
}

data class DetalleCalculo(
    val elemento: String,      // Ej: Eje A-A, Zapata Z-1
    val veces: Double = 1.0,   // N° elementos
    val largo: Double = 0.0,
    val ancho: Double = 0.0,
    val alto: Double = 0.0
) {
    // Parcial = Veces * L * A * H (adaptable según la unidad)
    val parcial: Double
        get() {
            var res = veces
            if (largo > 0) res *= largo
            if (ancho > 0) res *= ancho
            if (alto > 0) res *= alto
            return (res * 100).toLong() / 100.0 // Redondear a 2 decimales
        }
}