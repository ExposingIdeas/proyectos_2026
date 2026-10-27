// MetradoViewModel.kt
package com.example.metradosapp.viewmodel

import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import androidx.lifecycle.ViewModel
import com.example.metradosapp.model.*
import com.google.gson.GsonBuilder
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File

class MetradoViewModel : ViewModel() {

    private val _listaPartidas = MutableStateFlow<List<PartidaMetrado>>(emptyList())
    val listaPartidas = _listaPartidas.asStateFlow()

    fun agregarPartida(codigo: String, desc: String, unidad: String, detalle: DetalleCalculo) {
        val nuevaPartida = PartidaMetrado(
            codigoOE = codigo,
            descripcion = desc,
            unidad = unidad,
            detalles = listOf(detalle)
        )
        _listaPartidas.value = _listaPartidas.value + nuevaPartida
    }

    // Exportar y compartir archivo JSON
    fun exportarAJson(context: Context, nombreProyecto: String) {
        val proyecto = ProyectoMetrado(
            nombreProyecto = nombreProyecto,
            ubicacion = "Perú",
            metrados = _listaPartidas.value
        )

        val gson = GsonBuilder().setPrettyPrinting().create()
        val jsonString = gson.toJson(proyecto)

        try {
            // Guardar temporalmente en caché
            val file = File(context.cacheDir, "${nombreProyecto.replace(" ", "_")}_metrado.json")
            file.writeText(jsonString)

            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.provider",
                file
            )

            // Intent para compartir por Drive, WhatsApp, Email, etc.
            val sendIntent = Intent(Intent.ACTION_SEND).apply {
                type = "application/json"
                putExtra(Intent.EXTRA_STREAM, uri)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            context.startActivity(Intent.createChooser(sendIntent, "Exportar Metrado JSON"))
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    // Agrega esto dentro de la clase MetradoViewModel:

    // 1. Función para Eliminar
    fun eliminarPartida(id: String) {
        _listaPartidas.value = _listaPartidas.value.filter { it.id != id }
    }

    // 2. Función para Actualizar
    fun actualizarPartida(id: String, codigo: String, desc: String, unidad: String, detalle: DetalleCalculo) {
        _listaPartidas.value = _listaPartidas.value.map { partida ->
            if (partida.id == id) {
                partida.copy(
                    codigoOE = codigo,
                    descripcion = desc,
                    unidad = unidad,
                    detalles = listOf(detalle)
                )
            } else {
                partida
            }
        }
    }
}