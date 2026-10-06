# IPP original, 17 campos. La conversión del sistema no trae fuente, edad ni grupo.

IPP_TEST_ID = 2
REPORT_VIEWER_GROUPS = ['Administrador']
ESCALA_VERIFICADA_COMO_PERCENTIL = False
TRANSFORMED_LABEL = 'Puntuación transformada'

# Niveles del IPP. No se aplican mientras la conversión no esté verificada como percentil.
NIVELES_IPP = (
    (90, 99, 'Muy alto'),
    (75, 89, 'Alto'),
    (60, 74, 'Medio alto'),
    (40, 59, 'Medio'),
    (26, 39, 'Medio bajo'),
    (16, 25, 'Bajo'),
    (1, 15, 'Muy bajo'),
)

CAMPOS = (
    (1, 'Científico-Experimental', '1'),
    (2, 'Científico-Técnico', '2'),
    (3, 'Científico-Sanitario', '3'),
    (4, 'Teórico-Humanista', '4'),
    (5, 'Literario', '5'),
    (6, 'Psicopedagógico', '6'),
    (7, 'Político-Social', '7'),
    (8, 'Económico-Empresarial', '8'),
    (9, 'Persuasivo-Comercial', '9'),
    (10, 'Administrativo', '10'),
    (11, 'Deportivo', '11'),
    (12, 'Agropecuario', '12'),
    (13, 'Artístico-Musical', '13'),
    (14, 'Artístico-Plástico', '14'),
    (15, 'Militar-Seguridad', '15'),
    (16, 'Aventura-Riesgo', '16'),
    (17, 'Mecánico-Manual', '17'),
)

NOTA_ESCALA = (
    'La puntuación transformada es la salida actual de la conversión del sistema. '
    'No consta en el código la tabla, la edad ni el grupo del IPP original con los que se calculó. '
    'Por eso no se presenta como percentil. '
    'Tampoco se aplican los niveles 90–99 Muy alto, 75–89 Alto, 60–74 Medio alto, '
    '40–59 Medio, 26–39 Medio bajo, 16–25 Bajo y 1–15 Muy bajo.'
)

NOTA_PUNTAJE = (
    'El puntaje directo es la suma de las respuestas: A = 2, B = 1, C = 0 y D = 0. '
    'D significa que no conoce la actividad o la profesión y puntúa igual que el rechazo.'
)
