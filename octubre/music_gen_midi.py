from music21 import stream, note, chord, tempo, key, meter, instrument, metadata, roman

# ===== 1. Configuración de parámetros básicos =====
bpm = 80
total_bars = 60              # 60 compases ≈ 3 minutos a 80 BPM en 4/4

# ===== 2. Crear partitura y partes =====
score = stream.Score()
score.metadata = metadata.Metadata(
    title='Progresión C-G-Am-F',
    composer='Python Algorithm'
)

melody_part = stream.Part()
melody_part.append(instrument.Piano())
melody_part.append(tempo.MetronomeMark(number=bpm))
melody_part.append(meter.TimeSignature('4/4'))
melody_part.append(key.Key('C'))

chord_part = stream.Part()
chord_part.append(instrument.Piano())
chord_part.append(tempo.MetronomeMark(number=bpm))
chord_part.append(meter.TimeSignature('4/4'))
chord_part.append(key.Key('C'))

bass_part = stream.Part()
bass_part.append(instrument.ElectricBass())
bass_part.append(tempo.MetronomeMark(number=bpm))
bass_part.append(meter.TimeSignature('4/4'))
bass_part.append(key.Key('C'))

# ===== 3. Definir la progresión C - G - Am - F =====
# Cada acorde dura 1 compás. Se repite a lo largo de toda la pieza.
# Estructura: fundamental, tercera, quinta
progression = [
    {'name': 'C',  'pitches': ['C3', 'E3', 'G3'], 'bass': 'C2',
     'scale_notes': ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']},
    {'name': 'G',  'pitches': ['G3', 'B3', 'D4'], 'bass': 'G2',
     'scale_notes': ['G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5']},
    {'name': 'Am', 'pitches': ['A3', 'C4', 'E4'], 'bass': 'A2',
     'scale_notes': ['A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5']},
    {'name': 'F',  'pitches': ['F3', 'A3', 'C4'], 'bass': 'F2',
     'scale_notes': ['F4', 'G4', 'A4', 'Bb4', 'C5', 'D5', 'E5', 'F5']},
]

# ===== 4. Generar los 60 compases =====
for bar_num in range(total_bars):
    current = progression[bar_num % len(progression)]

    # --- Melodía: 4 negras por compás, usando notas de la escala del acorde ---
    # Patrón: nota del acorde, nota de paso, nota del acorde, nota de paso
    scale = current['scale_notes']
    chord_tone_indices = [0, 2, 4]  # grados 1, 3, 5 dentro de la escala
    for beat in range(4):
        if beat % 2 == 0:
            # Tiempo fuerte: nota del acorde
            idx = chord_tone_indices[(bar_num + beat) % len(chord_tone_indices)]
        else:
            # Tiempo débil: nota de paso
            idx = (bar_num * 2 + beat) % len(scale)
        n = note.Note(scale[idx])
        n.quarterLength = 1
        melody_part.append(n)

    # --- Acordes: un acorde por compás (redonda) ---
    c = chord.Chord(current['pitches'])
    c.quarterLength = 4
    chord_part.append(c)

    # --- Bajo: fundamental en negras, patrón raíz-quinta-raíz-quinta ---
    root = current['bass']
    # Calcular la quinta subiendo 7 semitonos (aproximación simple)
    fifth_note = note.Note(root)
    fifth_note.transpose(7, inPlace=True)
    bass_pattern = [root, fifth_note.nameWithOctave, root, fifth_note.nameWithOctave]
    for b in bass_pattern:
        bn = note.Note(b)
        bn.quarterLength = 1
        bass_part.append(bn)

# ===== 5. Ensamblar y exportar =====
score.append(melody_part)
score.append(chord_part)
score.append(bass_part)

score.write('midi', fp='cancion_CGAmF.mid')
print("MIDI generado: cancion_CGAmF.mid")

# ===== 6. (Opcional) Convertir a audio con FluidSynth =====
# Requiere: pip install midi2audio
# Y tener FluidSynth instalado + un SoundFont (.sf2)
# from midi2audio import FluidSynth
# fs = FluidSynth('ruta/a/FluidR3_GM.sf2')
# fs.midi_to_audio('cancion_CGAmF.mid', 'cancion_CGAmF.wav')