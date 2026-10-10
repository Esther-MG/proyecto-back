from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from usuarios_app.api.hspq_report import HspqReportJWTAuthentication
from usuarios_app.api.general_report_pdf import generate_general_pdf

from usuarios.models import User

from usuarios_app.api.dat_report import (
    build_dat_report,
    _can_view as dat_can_view,
)
from usuarios_app.api.dat_report_config import APTITUD_SIGNIFICADO
from usuarios_app.api.hspq_report_config import INTERPRETACION_PENDIENTE
from usuarios_app.api.ipp_report import (
    build_ipp_report,
    _can_view as ipp_can_view,
)
from usuarios_app.api.hspq_report import (
    build_hspq_report,
    _can_view as hspq_can_view,
)


def _unir(nombres):
    nombres = [nombre for nombre in nombres if nombre]
    if not nombres:
        return ''
    if len(nombres) == 1:
        return nombres[0]
    return ', '.join(nombres[:-1]) + ' y ' + nombres[-1]


def _nombre_estudiante(dat, ipp, hspq):
    for report in (dat, ipp, hspq):
        estudiante = report.get('estudiante') or {}
        nombre = (estudiante.get('nombre') or '').strip()
        if nombre:
            return nombre
    return 'Estudiante'


def _aptitud(item):
    nombre = item.get('nombre') or 'una aptitud'
    significado = APTITUD_SIGNIFICADO.get(item.get('codigo'))
    if significado:
        return f'{nombre}, es decir, {significado}'
    return nombre


def _grupos_aptitudes(subtests):
    """Ordena los centiles ya calculados por el informe de aptitudes. No recalcula puntajes."""
    disponibles = [item for item in subtests if item.get('centil') is not None]
    if not disponibles:
        return None
    mas_alto = max(item['centil'] for item in disponibles)
    mas_bajo = min(item['centil'] for item in disponibles)
    destacados = [item for item in disponibles if item['centil'] == mas_alto]
    bajos = [item for item in disponibles if item['centil'] == mas_bajo and item not in destacados]
    medio = [item for item in disponibles if item not in destacados and item not in bajos]
    ancla = max((item['centil'] for item in medio), default=None)
    altos = []
    intermedios = []
    if ancla is not None:
        for item in medio:
            mas_cerca_de_los_altos = (ancla - item['centil']) < (item['centil'] - mas_bajo)
            (altos if mas_cerca_de_los_altos or item['centil'] == ancla else intermedios).append(item)
    return destacados, altos, intermedios, bajos, mas_alto == mas_bajo


def _texto_aptitudes(dat):
    grupos = _grupos_aptitudes(dat.get('subtests') or [])
    if not grupos:
        return ['No hay resultados de aptitudes para explicar esta parte.']
    destacados, altos, intermedios, bajos, planos = grupos
    if planos:
        return [
            'Tus aptitudes quedaron en el mismo punto. Dentro de tu perfil no se ve una más alta ni una más baja.',
        ]
    partes = [
        'Lo que más se destaca en tus aptitudes es '
        + _unir(_aptitud(item) for item in destacados)
        + '. Dentro de tu perfil, eso queda por encima de tus otras aptitudes. '
        'No significa una capacidad fija ni una imposibilidad en las demás.',
    ]
    if altos:
        partes.append(
            'También quedan por encima de la mayoría de tus aptitudes, aunque no son las más altas: '
            + _unir(_aptitud(item) for item in altos)
            + '.'
        )
    if intermedios:
        partes.append(
            'Quedan en medio de tu perfil, más cerca de los resultados bajos que de los altos: '
            + _unir(_aptitud(item) for item in intermedios)
            + '.'
        )
    if bajos:
        cierre = (
            'Es un resultado menor solo en comparación con tus otras aptitudes.'
            if len(bajos) == 1 else
            'Son resultados menores solo en comparación con tus otras aptitudes.'
        )
        partes.append(
            'Lo que queda más abajo en tu perfil es '
            + _unir(_aptitud(item) for item in bajos)
            + '. '
            + cierre
        )
    return partes


def _texto_intereses(ipp):
    campos = [
        item for item in (ipp.get('campos') or [])
        if item.get('pt_ac') is not None and item.get('pt_pr') is not None
    ]
    if not campos:
        return ['No hay resultados de intereses para explicar esta parte.']

    def extremos(clave, mayor):
        valor = max(item[clave] for item in campos) if mayor else min(item[clave] for item in campos)
        return [item for item in campos if item[clave] == valor]

    actividades_altas = extremos('pt_ac', True)
    actividades_bajas = extremos('pt_ac', False)
    profesiones_altas = extremos('pt_pr', True)
    profesiones_bajas = extremos('pt_pr', False)
    def frase_interes(mayor, tema, items):
        nombres = [item['nombre'] for item in items]
        nivel = 'mayor' if mayor else 'menor'
        return f'El {nivel} interés por las {tema} aparece en {_unir(nombres)}.'

    partes = [
        frase_interes(True, 'actividades', actividades_altas),
        frase_interes(True, 'profesiones', profesiones_altas),
        frase_interes(False, 'actividades', actividades_bajas),
        frase_interes(False, 'profesiones', profesiones_bajas),
    ]
    puntajes = [item[clave] for item in campos for clave in ('pt_ac', 'pt_pr')]
    amplitud = max(puntajes) - min(puntajes)
    separaciones = sorted(
        (
            (abs(item['pt_ac'] - item['pt_pr']), item['pt_ac'] - item['pt_pr'], item)
            for item in campos
        ),
        key=lambda fila: fila[0],
        reverse=True,
    )
    corte = amplitud / 2
    discrepantes = [fila for fila in separaciones if fila[0] >= corte and fila[0] > 0]
    if not discrepantes and separaciones and separaciones[0][0] > 0:
        discrepantes = [separaciones[0]]
    if discrepantes:
        for _diferencia, delta, item in discrepantes:
            if delta > 0:
                partes.append(
                    f"En {item['nombre']}, el interés por las actividades es mayor que el interés por las profesiones de ese mismo campo."
                )
            else:
                partes.append(
                    f"En {item['nombre']}, el interés por las profesiones es mayor que el interés por las actividades de ese mismo campo."
                )
        partes.append(
            'Esa diferencia solo compara las dos partes del mismo campo. No elige una opción de estudio.'
        )
    else:
        partes.append(
            'En tu perfil, el gusto por las actividades y por las profesiones queda bastante parecido en cada campo.'
        )
    cercanas = [fila for fila in separaciones if fila[0] == separaciones[-1][0]]
    partes.append(
        'Las actividades y las profesiones se parecen más en '
        + _unir(item['nombre'] for _diferencia, _delta, item in cercanas)
        + '.'
    )
    desconocidos = [
        item for item in campos
        if item.get('desconocidas_ac') or item.get('desconocidas_pr')
    ]
    bajos = {item['id'] for item in actividades_bajas + profesiones_bajas}
    desconocidos_bajos = [item for item in desconocidos if item['id'] in bajos]
    if desconocidos_bajos:
        partes.append(
            'En '
            + _unir(item['nombre'] for item in desconocidos_bajos)
            + ' marcaste que no conocías alguna actividad o profesión. '
            'Esa respuesta cuenta igual que “no me gusta”, así que un resultado bajo no distingue '
            'desconocimiento de desagrado.'
        )
    return partes


# Misma descripción del HSPQ, dicha en lenguaje sencillo. No agrega rasgos nuevos.
_EXPLICACION_HSPQ = {
    'Reservado, alejado, crítico, frío': 'Te muestras más reservado, distante y crítico.',
    'Abierto, afectuoso, reposado, participativo, sociable': 'Te muestras más abierto, cercano, participativo y sociable.',
    'Bajo en inteligencia, pensamiento concreto': 'Predomina un pensamiento más concreto que abstracto.',
    'Alto en inteligencia, pensamiento abstracto, brillante': 'Predomina un pensamiento más abstracto.',
    'Afectado por sentimientos, emocionalmente poco estable, turbable': 'Te afectan más los sentimientos y te notas menos estable.',
    'Emocionalmente estable, tranquilo, maduro, afronta la realidad': 'Te muestras más estable, tranquilo y capaz de afrontar la realidad.',
    'Calmoso, poco expresivo, cauto, poco activo': 'Te muestras más calmo, cauto y poco expresivo.',
    'Excitable, impaciente, exigente, hiperactivo, no inhibido': 'Te muestras más excitable, impaciente y activo.',
    'Sumiso, obediente, dócil, acomodaticio': 'Te muestras más sumiso, obediente y dócil.',
    'Dominante, dogmático, agresivo, obstinado': 'Te muestras más dominante y obstinado.',
    'Sobrio, prudente, serio, taciturno': 'Te muestras más serio, prudente y sobrio.',
    'Entusiasta, incauto, confiado a la buena ventura': 'Te muestras más entusiasta y confiado.',
    'Despreocupado o desatento con las normas': 'Te muestras más despreocupado frente a las normas.',
    'Consciente, perseverante, moralista, sensato, sujeto a normas': 'Te muestras más perseverante y atento a las normas.',
    'Cohibido, tímido, sensible a la amenaza': 'Te muestras más tímido y cohibido.',
    'Emprendedor, socialmente atrevido, no inhibido': 'Te muestras más emprendedor y atrevido al tratar con los demás.',
    'Sensibilidad dura, poco impresionable': 'Te muestras menos impresionable.',
    'Sensibilidad blanda, impresionable, con simpatía por las necesidades de los demás': 'Te muestras más sensible e impresionable, y con más atención a las necesidades de los demás.',
    'Seguro, gusto por la actividad en grupo': 'Te muestras más seguro y con gusto por la actividad en grupo.',
    'Dubitativo, irresoluto, reservado, individualista': 'Te muestras más dubitativo, reservado e individualista.',
    'Sereno, apacible, confiado, seguro de sí mismo': 'Te muestras más sereno y seguro de ti mismo.',
    'Aprensivo, con sensación de culpabilidad, inseguro, preocupado': 'Te muestras más aprensivo, inseguro y preocupado.',
    'Sociable, buen compañero y de fácil unión al grupo': 'Te resulta más fácil unirte al grupo.',
    'Autosuficiente, prefiere sus propias decisiones, lleno de recursos': 'Prefieres decidir por tu cuenta y te muestras más autosuficiente.',
    'Poco integrado, descuidado, autoconflictivo': 'Te muestras menos organizado y más descuidado.',
    'Muy integrado, socialmente escrupuloso, autodisciplinado': 'Te muestras más autodisciplinado y cuidadoso en lo social.',
    'Relajado, tranquilo, pesado, sosegado': 'Te muestras más relajado y tranquilo.',
    'Tenso, frustrado, presionado, sobreexcitado, inquieto': 'Te muestras más tenso e inquieto.',
}


def _explicar_hspq(descripcion):
    clave = (descripcion or '').strip().rstrip('.')
    return _EXPLICACION_HSPQ.get(clave, descripcion)


def _frase_natural_hspq(texto):
    base = (texto or '').strip().rstrip('.')
    if base.startswith('Predomina '):
        resto = base[len('Predomina '):]
        resto = resto[:1].lower() + resto[1:]
        return f'En este aspecto, tus resultados indican una tendencia hacia {resto}.'
    inicio = base[:1].lower() + base[1:]
    return f'En este aspecto, tus resultados indican que {inicio}.'


def _factores_destacados(hspq):
    factores = [
        item for item in (hspq.get('factores_primarios') or [])
        if item.get('descripcion') and item.get('descripcion') != INTERPRETACION_PENDIENTE
        and item.get('nivel') in ('alto', 'bajo')
    ]

    def frases(nivel):
        return [
            _explicar_hspq(item['descripcion']).rstrip('.')
            for item in factores
            if item.get('nivel') == nivel
        ]

    return frases('alto'), frases('bajo')


def _texto_personalidad(hspq):
    altos, bajos = _factores_destacados(hspq)
    if not altos and not bajos:
        return ['En este cuestionario no hay características que se alejen del punto medio.']

    partes = [
        'Solo se comentan las características que se alejan del punto medio en tus resultados. '
        'No es un diagnóstico.',
    ]
    partes.extend(_frase_natural_hspq(frase) for frase in altos + bajos)
    return partes


def _personalidad_para_conjunto(hspq):
    """Mantiene los títulos que ya usa la lectura conjunta. No se muestra al estudiante."""
    altos, bajos = _factores_destacados(hspq)
    partes = []
    if altos:
        partes.append('En el extremo alto, el cuestionario te describe así:')
        partes.extend(f'{frase}.' for frase in altos)
    if bajos:
        partes.append('En el extremo bajo, el cuestionario te describe así:')
        partes.extend(f'{frase}.' for frase in bajos)
    return partes


def _frases_despues(parrafos, titulo):
    frases = []
    tomando = False
    for texto in parrafos:
        if texto == titulo:
            tomando = True
            continue
        if not tomando:
            continue
        if texto.endswith(':') or texto.startswith('En un punto medio'):
            break
        frases.append(texto.rstrip('.'))
    return frases


def _texto_conjunto(nombre, aptitudes, intereses, personalidad):
    altos = _frases_despues(personalidad, 'En el extremo alto, el cuestionario te describe así:')
    bajos = _frases_despues(personalidad, 'En el extremo bajo, el cuestionario te describe así:')
    personalidad_texto = ''
    if altos:
        personalidad_texto += ' En personalidad, el extremo alto se describe como ' + _unir(altos) + '.'
    if bajos:
        personalidad_texto += ' El extremo bajo se describe como ' + _unir(bajos) + '.'
    return [
        f'{nombre}, estas tres partes se leen juntas, pero cada una dice algo distinto. '
        + aptitudes[0]
        + ' '
        + intereses[0]
        + ' '
        + intereses[1]
        + personalidad_texto,
        'Este resumen no elige una opción de estudio ni describe un problema. '
        'Sirve para conversarlo con el profesional que acompaña la orientación.',
    ]


def _interpretacion_general(dat, ipp, hspq):
    nombre = _nombre_estudiante(dat, ipp, hspq)
    aptitudes = _texto_aptitudes(dat)
    intereses = _texto_intereses(ipp)
    personalidad = _texto_personalidad(hspq)
    conjunto = _texto_conjunto(nombre, aptitudes, intereses, _personalidad_para_conjunto(hspq))
    nota = (
        'Estos resultados orientan la conversación. No son un diagnóstico y no determinan '
        'por sí solos una elección de estudio.'
    )
    return {
        'nombre': nombre,
        'introduccion': (
            f'{nombre}, este informe explica tus propios resultados con palabras sencillas. '
            'Compara lo que obtuviste dentro de cada prueba.'
        ),
        'aptitudes': aptitudes,
        'intereses': intereses,
        'personalidad': personalidad,
        'conjunto': conjunto,
        'dat': ' '.join(aptitudes),
        'ipp': ' '.join(intereses),
        'hspq': ' '.join(personalidad),
        'resumen_general': ' '.join(conjunto),
        'conclusion': nota,
    }


def build_general_report(user):
    dat = build_dat_report(user)
    ipp = build_ipp_report(user)
    hspq = build_hspq_report(user)

    return {
        'estudiante': dat.get('estudiante') or ipp.get('estudiante') or hspq.get('estudiante'),

        'tests': {
            'dat': dat,
            'ipp': ipp,
            'hspq': hspq,
        },

        'interpretacion_general': _interpretacion_general(
            dat,
            ipp,
            hspq,
        ),
    }


class GeneralReportDataView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)

        if not dat_can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)

        return Response(build_general_report(user))


class GeneralReportPdfView(APIView):
    authentication_classes = [HspqReportJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        if not dat_can_view(request.user, user):
            return Response({'detail': 'No autorizado.'}, status=403)
        pdf = generate_general_pdf(build_general_report(user))
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Informe_General_{user_id}.pdf"'
        return response