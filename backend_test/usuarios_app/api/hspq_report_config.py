FACTOR_ORDER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']

# Grupos autorizados a consultar el informe de otro usuario (ademas del propio estudiante).
REPORT_VIEWER_GROUPS = ['Administrador']

DECATIPO_SOURCE_NOTE = (
    "Decatipos calculados con las funciones convert_section_* de usuarios_app/api/views.py "
    "(baremo unico, sin distincion de sexo ni edad). No verificado contra el manual del HSPQ."
)

# Factores de personalidad que alimentan los secundarios QI-QIV (Tabla 4). B queda excluido
# porque es la escala de habilidad mental, no una escala de personalidad.
SECONDARY_SOURCE_FACTORS = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']

SECONDARY_FACTOR_NAMES = {
    'QI': 'Ajuste - Ansiedad',
    'QII': 'Introversión - Extraversión',
    'QIII': 'Calma - Excitabilidad',
    'QIV': 'Dependencia - Independencia',
}

SECONDARY_FACTORS_SOURCE_NOTE = (
    "Factores secundarios QI-QIV calculados con D' = sum(Ki * Di) + a, usando los decatipos "
    "de los 13 factores de personalidad (sin B) y los coeficientes de la Tabla 4 (adaptacion "
    "espanola del manual HSPQ) proporcionados por el usuario, diferenciados por sexo."
)

# Coeficientes de la Tabla 4, provistos por el usuario a partir del manual HSPQ (adaptacion
# espanola). Expresados ya en decimal (el manual los presenta en centesimas).
SECONDARY_FACTOR_COEFFICIENTS = {
    'masculino': {
        'QI': {
            'A': -0.03, 'C': -0.21, 'D': 0.06, 'E': 0.02, 'F': 0.10, 'G': -0.38,
            'H': -0.11, 'I': -0.03, 'J': 0.00, 'O': 0.15, 'Q2': -0.04, 'Q3': -0.29,
            'Q4': 0.03, 'constante': 9.52,
        },
        'QII': {
            'A': 0.21, 'C': 0.08, 'D': -0.03, 'E': -0.09, 'F': 0.16, 'G': -0.06,
            'H': 0.28, 'I': 0.01, 'J': -0.17, 'O': -0.07, 'Q2': -0.34, 'Q3': 0.01,
            'Q4': -0.02, 'constante': 5.67,
        },
        'QIII': {
            'A': 0.05, 'C': -0.11, 'D': 0.42, 'E': -0.10, 'F': 0.09, 'G': 0.14,
            'H': -0.06, 'I': -0.02, 'J': -0.01, 'O': 0.12, 'Q2': -0.14, 'Q3': -0.02,
            'Q4': 0.32, 'constante': 1.76,
        },
        'QIV': {
            'A': -0.06, 'C': 0.14, 'D': 0.15, 'E': 0.33, 'F': 0.23, 'G': -0.11,
            'H': 0.22, 'I': -0.21, 'J': 0.10, 'O': -0.06, 'Q2': 0.04, 'Q3': 0.14,
            'Q4': -0.11, 'constante': 2.64,
        },
    },
    'femenino': {
        'QI': {
            'A': 0.00, 'C': -0.27, 'D': 0.15, 'E': -0.04, 'F': 0.08, 'G': -0.24,
            'H': -0.17, 'I': -0.02, 'J': 0.01, 'O': 0.18, 'Q2': -0.03, 'Q3': -0.23,
            'Q4': 0.13, 'constante': 7.98,
        },
        'QII': {
            'A': 0.30, 'C': 0.02, 'D': -0.01, 'E': -0.07, 'F': 0.17, 'G': -0.05,
            'H': 0.20, 'I': 0.02, 'J': -0.18, 'O': -0.04, 'Q2': -0.37, 'Q3': -0.02,
            'Q4': 0.02, 'constante': 5.56,
        },
        'QIII': {
            'A': -0.05, 'C': 0.07, 'D': 0.51, 'E': -0.01, 'F': 0.05, 'G': 0.32,
            'H': -0.06, 'I': 0.04, 'J': 0.09, 'O': 0.03, 'Q2': -0.09, 'Q3': 0.08,
            'Q4': 0.24, 'constante': -1.21,
        },
        'QIV': {
            'A': -0.08, 'C': 0.12, 'D': 0.12, 'E': 0.24, 'F': 0.28, 'G': -0.25,
            'H': 0.26, 'I': -0.19, 'J': 0.09, 'O': -0.07, 'Q2': 0.07, 'Q3': -0.14,
            'Q4': -0.11, 'constante': 3.63,
        },
    },
}

# Valores aceptados de User.sexo (campo de texto libre) mapeados a las tablas de coeficientes.
SEXO_ALIASES = {
    'm': 'masculino', 'masculino': 'masculino', 'hombre': 'masculino', 'varon': 'masculino',
    'varón': 'masculino', 'h': 'masculino',
    'f': 'femenino', 'femenino': 'femenino', 'mujer': 'femenino',
}

# Umbral de nivel segun el decatipo: <=3 bajo, 4-7 promedio, >=8 alto. Se aplica igual a
# los 14 factores primarios y, de forma aproximada, a los secundarios QI-QIV (escala continua).
NIVEL_BAJO_MAX = 3
NIVEL_PROMEDIO_MAX = 7

# Texto usado cuando no existe en el proyecto una descripcion interpretativa verificada contra
# una fuente oficial del HSPQ. No debe reemplazarse por texto inventado.
INTERPRETACION_PENDIENTE = "Interpretación pendiente de fuente oficial."

# Descriptores de polos por factor primario, Cuadro B del manual HSPQ (adaptacion espanola).
# Se aplican segun el nivel del decatipo: bajo (<=3) o alto (>=8). B es la escala de habilidad
# mental; los demas son las 13 escalas de personalidad usadas tambien en QI-QIV.
FACTOR_POLE_DESCRIPTIONS = {
    'A': {
        'bajo': 'Reservado, alejado, crítico, frío.',
        'alto': 'Abierto, afectuoso, reposado, participativo, sociable.',
    },
    'B': {
        'bajo': 'Bajo en inteligencia, pensamiento concreto.',
        'alto': 'Alto en inteligencia, pensamiento abstracto, brillante.',
    },
    'C': {
        'bajo': 'Afectado por sentimientos, emocionalmente poco estable, turbable.',
        'alto': 'Emocionalmente estable, tranquilo, maduro, afronta la realidad.',
    },
    'D': {
        'bajo': 'Calmoso, poco expresivo, cauto, poco activo.',
        'alto': 'Excitable, impaciente, exigente, hiperactivo, no inhibido.',
    },
    'E': {
        'bajo': 'Sumiso, obediente, dócil, acomodaticio.',
        'alto': 'Dominante, dogmático, agresivo, obstinado.',
    },
    'F': {
        'bajo': 'Sobrio, prudente, serio, taciturno.',
        'alto': 'Entusiasta, incauto, confiado a la buena ventura.',
    },
    'G': {
        'bajo': 'Despreocupado o desatento con las normas.',
        'alto': 'Consciente, perseverante, moralista, sensato, sujeto a normas.',
    },
    'H': {
        'bajo': 'Cohibido, tímido, sensible a la amenaza.',
        'alto': 'Emprendedor, socialmente atrevido, no inhibido.',
    },
    'I': {
        'bajo': 'Sensibilidad dura, poco impresionable.',
        'alto': 'Sensibilidad blanda, impresionable, con simpatía por las necesidades de los demás.',
    },
    'J': {
        'bajo': 'Seguro, gusto por la actividad en grupo.',
        'alto': 'Dubitativo, irresoluto, reservado, individualista.',
    },
    'O': {
        'bajo': 'Sereno, apacible, confiado, seguro de sí mismo.',
        'alto': 'Aprensivo, con sensación de culpabilidad, inseguro, preocupado.',
    },
    'Q2': {
        'bajo': 'Sociable, buen compañero y de fácil unión al grupo.',
        'alto': 'Autosuficiente, prefiere sus propias decisiones, lleno de recursos.',
    },
    'Q3': {
        'bajo': 'Poco integrado, descuidado, autoconflictivo.',
        'alto': 'Muy integrado, socialmente escrupuloso, autodisciplinado.',
    },
    'Q4': {
        'bajo': 'Relajado, tranquilo, pesado, sosegado.',
        'alto': 'Tenso, frustrado, presionado, sobreexcitado, inquieto.',
    },
}
