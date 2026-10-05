# Baremo de la imagen aportada: Tabla 42, 2.º Bachillerato.
# Solo VR, NR, AR, MR, SR, OR y PSA. VR+NR, S y De no se calculan.
# Un guion de la imagen no se rellena ni se interpola.

DAT_TEST_ID = 1
REPORT_VIEWER_GROUPS = ['Administrador']

BAREMO_FUENTE = 'Plantilla de Baremos escolares'
BAREMO_NOTA_SEXO = (
    'La plantilla aplicada no separa estas siete columnas por sexo. '
    'Se usa la misma equivalencia para el puntaje directo.'
)
NO_CONVERSION_NOTE = (
    'El centil no es la conversión 1-99 del sistema. Sale de la Plantilla de Baremos escolares.'
)

# Significado de cada aptitud del DAT. No es un nivel ni una recomendación.
APTITUD_SIGNIFICADO = {
    'VR': 'manejo de conceptos y relaciones expresadas con palabras',
    'NR': 'relaciones y operaciones numéricas',
    'AR': 'identificación de patrones no verbales',
    'MR': 'comprensión de principios físicos y mecánicos',
    'SR': 'visualización de formas y posiciones en el espacio',
    'OR': 'reconocimiento de la forma escrita correcta',
    'PSA': 'comparación visual rápida y precisa',
}

SUBTESTS = (
    (1, 'VR'),
    (2, 'NR'),
    (3, 'AR'),
    (4, 'MR'),
    (5, 'SR'),
    (6, 'OR'),
    (7, 'PSA'),
)


def _cells(pairs):
    rows = []
    for centil, text in pairs:
        if text == '-':
            continue
        if '-' in text:
            low, high = text.split('-')
            rows.append((centil, int(low), int(high)))
        else:
            value = int(text)
            rows.append((centil, value, value))
    return tuple(rows)


TABLA_42 = {
    'VR': _cells((
        (99, '35-40'), (98, '34'), (97, '33'), (96, '32'), (95, '-'),
        (90, '29-31'), (85, '27-28'), (80, '26'), (75, '25'), (70, '24'),
        (65, '23'), (60, '-'), (55, '22'), (50, '21'), (45, '-'),
        (40, '20'), (35, '19'), (30, '18'), (25, '17'), (20, '16'),
        (15, '15'), (10, '13-14'), (5, '12'), (4, '11'), (3, '-'),
        (2, '10'), (1, '0-9'),
    )),
    'NR': _cells((
        (99, '32-40'), (98, '30-31'), (97, '29'), (96, '-'), (95, '27-28'),
        (90, '22-26'), (85, '20-21'), (80, '19'), (75, '18'), (70, '17'),
        (65, '-'), (60, '16'), (55, '15'), (50, '-'), (45, '14'),
        (40, '13'), (35, '12'), (30, '-'), (25, '11'), (20, '10'),
        (15, '9'), (10, '7-8'), (5, '6'), (4, '-'), (3, '5'),
        (2, '-'), (1, '0-4'),
    )),
    'AR': _cells((
        (99, '36-40'), (98, '-'), (97, '-'), (96, '35'), (95, '34'),
        (90, '31-33'), (85, '29-30'), (80, '28'), (75, '26-27'), (70, '25'),
        (65, '-'), (60, '24'), (55, '22-23'), (50, '-'), (45, '21'),
        (40, '19-20'), (35, '18'), (30, '17'), (25, '16'), (20, '15'),
        (15, '13-14'), (10, '11-12'), (5, '-'), (4, '10'), (3, '9'),
        (2, '8'), (1, '0-7'),
    )),
    'MR': _cells((
        (99, '54-60'), (98, '52-53'), (97, '51'), (96, '-'), (95, '50'),
        (90, '47-49'), (85, '45-46'), (80, '43-44'), (75, '40-42'), (70, '38-39'),
        (65, '-'), (60, '37'), (55, '32-36'), (50, '-'), (45, '31'),
        (40, '28-30'), (35, '27'), (30, '26'), (25, '24-25'), (20, '23'),
        (15, '22'), (10, '21'), (5, '18-20'), (4, '17'), (3, '16'),
        (2, '14-15'), (1, '0-13'),
    )),
    'SR': _cells((
        (99, '47-50'), (98, '45-46'), (97, '44'), (96, '41-43'), (95, '40'),
        (90, '38-39'), (85, '36-37'), (80, '34-35'), (75, '32-33'), (70, '30-31'),
        (65, '29'), (60, '28'), (55, '26-27'), (50, '25'), (45, '24'),
        (40, '21-23'), (35, '19-20'), (30, '18'), (25, '17'), (20, '15-16'),
        (15, '14'), (10, '12-13'), (5, '8-11'), (4, '7'), (3, '6'),
        (2, '5'), (1, '0-4'),
    )),
    'OR': _cells((
        (99, '40'), (98, '39'), (97, '-'), (96, '38'), (95, '-'),
        (90, '37'), (85, '36'), (80, '35'), (75, '-'), (70, '34'),
        (65, '-'), (60, '33'), (55, '31-32'), (50, '-'), (45, '30'),
        (40, '28-29'), (35, '-'), (30, '27'), (25, '26'), (20, '25'),
        (15, '22-24'), (10, '20-21'), (5, '18-19'), (4, '17'), (3, '16'),
        (2, '14-15'), (1, '0-13'),
    )),
    'PSA': _cells((
        (99, '94-100'), (98, '90-93'), (97, '87-89'), (96, '85-86'), (95, '83-84'),
        (90, '75-82'), (85, '70-74'), (80, '68-69'), (75, '65-67'), (70, '63-64'),
        (65, '62'), (60, '61'), (55, '57-60'), (50, '-'), (45, '56'),
        (40, '54-55'), (35, '53'), (30, '52'), (25, '50-51'), (20, '46-49'),
        (15, '45'), (10, '42-44'), (5, '39-41'), (4, '38'), (3, '37'),
        (2, '32-36'), (1, '0-31'),
    )),
}


def lookup_centil(code, raw_score):
    """Devuelve (centil, observacion). No inventa equivalencias."""
    if raw_score is None:
        return None, 'Sin puntaje directo.'
    try:
        score = int(raw_score)
    except (TypeError, ValueError):
        return None, 'Puntaje directo no numérico.'
    if score != raw_score:
        return None, 'La plantilla no define centil para un puntaje no entero.'
    matches = [
        centil for centil, low, high in TABLA_42.get(code, ())
        if low <= score <= high
    ]
    if len(matches) == 1:
        return matches[0], 'Equivalencia de la plantilla.'
    if len(matches) > 1:
        return None, 'El puntaje aparece en más de una celda de la plantilla.'
    return None, 'El puntaje directo no aparece en la plantilla.'

