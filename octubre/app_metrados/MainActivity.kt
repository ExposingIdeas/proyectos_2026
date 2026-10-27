package com.example.metradosapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.metradosapp.model.DetalleCalculo
import com.example.metradosapp.model.PartidaMetrado
import com.example.metradosapp.viewmodel.MetradoViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                MetradoScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MetradoScreen(vm: MetradoViewModel = viewModel()) {
    val context = LocalContext.current
    val partidas by vm.listaPartidas.collectAsState()

    // Estado para controlar si estamos creando o editando
    var idEnEdicion by remember { mutableStateOf<String?>(null) }

    // Estados del formulario
    var codigoOE by remember { mutableStateOf("OE.2.3.1") }
    var descripcion by remember { mutableStateOf("") }
    var unidad by remember { mutableStateOf("m3") }
    var elemento by remember { mutableStateOf("") }
    var veces by remember { mutableStateOf("1") }
    var largo by remember { mutableStateOf("") }
    var ancho by remember { mutableStateOf("") }
    var alto by remember { mutableStateOf("") }

    // Función auxiliar para limpiar formulario
    fun limpiarFormulario() {
        idEnEdicion = null
        codigoOE = "OE.2.3.1"
        descripcion = ""
        elemento = ""
        veces = "1"
        largo = ""
        ancho = ""
        alto = ""
    }

    Scaffold(
        topBar = { TopAppBar(title = { Text("Metrados (Norma Peruana)") }) },
        bottomBar = {
            Button(
                onClick = { vm.exportarAJson(context, "Obra_Vivienda_Unifamiliar") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                enabled = partidas.isNotEmpty()
            ) {
                Text("Exportar a JSON")
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .padding(16.dp)
                .fillMaxSize()
        ) {
            Text(
                text = if (idEnEdicion == null) "Nueva Partida" else "Editando Partida",
                style = MaterialTheme.typography.titleMedium,
                color = if (idEnEdicion == null) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
            )

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = codigoOE,
                    onValueChange = { codigoOE = it },
                    label = { Text("Cód. OE") },
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = unidad,
                    onValueChange = { unidad = it },
                    label = { Text("Unid.") },
                    modifier = Modifier.weight(1f)
                )
            }

            OutlinedTextField(
                value = descripcion,
                onValueChange = { descripcion = it },
                label = { Text("Descripción (Ej: Concreto Zapata)") },
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = elemento,
                onValueChange = { elemento = it },
                label = { Text("Elemento/Eje (Ej: Zapata Z-1)") },
                modifier = Modifier.fillMaxWidth()
            )

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = veces,
                    onValueChange = { veces = it },
                    label = { Text("N° Veces") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = largo,
                    onValueChange = { largo = it },
                    label = { Text("Largo (m)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
            }

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = ancho,
                    onValueChange = { ancho = it },
                    label = { Text("Ancho (m)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = alto,
                    onValueChange = { alto = it },
                    label = { Text("Alto (m)") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
            }

            // Botones de acción del formulario (Registrar / Actualizar / Cancelar)
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Button(
                    onClick = {
                        val det = DetalleCalculo(
                            elemento = elemento.ifEmpty { "General" },
                            veces = veces.toDoubleOrNull() ?: 1.0,
                            largo = largo.toDoubleOrNull() ?: 0.0,
                            ancho = ancho.toDoubleOrNull() ?: 0.0,
                            alto = alto.toDoubleOrNull() ?: 0.0
                        )

                        if (idEnEdicion == null) {
                            vm.agregarPartida(codigoOE, descripcion, unidad, det)
                        } else {
                            vm.actualizarPartida(idEnEdicion!!, codigoOE, descripcion, unidad, det)
                        }
                        limpiarFormulario()
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text(if (idEnEdicion == null) "Registrar Metrado" else "Guardar Cambios")
                }

                if (idEnEdicion != null) {
                    OutlinedButton(
                        onClick = { limpiarFormulario() },
                        modifier = Modifier.weight(0.7f)
                    ) {
                        Text("Cancelar")
                    }
                }
            }

            Divider(modifier = Modifier.padding(vertical = 8.dp))

            // LISTA DE METRADOS CON ACCIONES DE EDITAR Y BORRAR
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(partidas) { p ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "${p.codigoOE} - ${p.descripcion}",
                                    style = MaterialTheme.typography.titleSmall
                                )
                                Text(
                                    text = "Total: ${p.total} ${p.unidad}",
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }

                            // Botón Editar
                            IconButton(onClick = {
                                idEnEdicion = p.id
                                codigoOE = p.codigoOE
                                descripcion = p.descripcion
                                unidad = p.unidad
                                val det = p.detalles.firstOrNull()
                                elemento = det?.elemento ?: ""
                                veces = det?.veces?.toString() ?: "1"
                                largo = det?.largo?.toString() ?: ""
                                ancho = det?.ancho?.toString() ?: ""
                                alto = det?.alto?.toString() ?: ""
                            }) {
                                Icon(
                                    imageVector = Icons.Default.Edit,
                                    contentDescription = "Editar",
                                    tint = MaterialTheme.colorScheme.secondary
                                )
                            }

                            // Botón Eliminar
                            IconButton(onClick = {
                                vm.eliminarPartida(p.id)
                                if (idEnEdicion == p.id) {
                                    limpiarFormulario()
                                }
                            }) {
                                Icon(
                                    imageVector = Icons.Default.Delete,
                                    contentDescription = "Eliminar",
                                    tint = MaterialTheme.colorScheme.error
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}