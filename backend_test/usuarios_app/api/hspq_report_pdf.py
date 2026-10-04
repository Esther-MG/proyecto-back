import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

NAVY = colors.HexColor('#1F4E79')
NAVY_SOFT = colors.HexColor('#E7EEF5')
LINE = colors.HexColor('#C5D0DC')
MUTED = colors.HexColor('#5B6770')
ROW_ALT = colors.HexColor('#F7F9FB')

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 16 * mm
RIGHT_MARGIN = 16 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

PROFILE_FACTORS = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'O', 'Q2', 'Q3', 'Q4']

FINAL_NOTE = (
    "Este informe presenta resultados descriptivos del HSPQ y debe ser interpretado "
    "por un profesional. No constituye un diagnóstico."
)


def _text(value):
    if value is None or value == '':
        return 'No disponible'
    return escape(str(value))


def _styles():
    base = getSampleStyleSheet()
    styles = {
        'title': ParagraphStyle(
            'HspqTitle', parent=base['Title'], fontName='Helvetica-Bold',
            fontSize=16, leading=19, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2,
        ),
        'subtitle': ParagraphStyle(
            'HspqSubtitle', parent=base['Normal'], fontName='Helvetica',
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=8,
        ),
        'section': ParagraphStyle(
            'HspqSection', parent=base['Heading2'], fontName='Helvetica-Bold',
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=6,
        ),
        'body': ParagraphStyle(
            'HspqBody', parent=base['Normal'], fontName='Helvetica',
            fontSize=9, leading=12, textColor=colors.black,
        ),
        'small': ParagraphStyle(
            'HspqSmall', parent=base['Normal'], fontName='Helvetica',
            fontSize=8, leading=10, textColor=colors.black,
        ),
        'note': ParagraphStyle(
            'HspqNote', parent=base['Normal'], fontName='Helvetica-Oblique',
            fontSize=8, leading=11, textColor=colors.black, alignment=TA_JUSTIFY,
        ),
        'header_cell': ParagraphStyle(
            'HspqHeaderCell', parent=base['Normal'], fontName='Helvetica-Bold',
            fontSize=8, leading=10, textColor=colors.white,
        ),
        'cell': ParagraphStyle(
            'HspqCell', parent=base['Normal'], fontName='Helvetica',
            fontSize=7.5, leading=9.5, textColor=colors.black,
        ),
    }
    return styles


def _section(styles, title):
    return Paragraph(title, styles['section'])


def _kv_table(rows):
    data = [[Paragraph(f'<b>{escape(label)}</b>', _styles()['small']),
             Paragraph(_text(value), _styles()['small'])] for label, value in rows]
    table = Table(data, colWidths=[42 * mm, CONTENT_WIDTH - 42 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), NAVY_SOFT),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.3, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table


def _completitud_text(completitud):
    if not completitud:
        return 'No disponible'
    pendientes = [item.get('factor') for item in completitud if item.get('estado') != 'completo']
    if not pendientes:
        return 'Completo en los 14 factores primarios'
    detalle = ', '.join(str(factor) for factor in pendientes if factor)
    return f'Incompleto en: {detalle}' if detalle else 'Incompleto'


class HspqProfileChart(Flowable):
    """Perfil de las 13 escalas de personalidad. No incluye B."""

    def __init__(self, series, height=198):
        super().__init__()
        by_factor = {item.get('factor'): item.get('decatipo') for item in series or []}
        self.labels = PROFILE_FACTORS
        self.values = [by_factor.get(factor) for factor in PROFILE_FACTORS]
        self.chart_height = height

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.chart_height

    def draw(self):
        canvas = self.canv
        left = 28
        bottom = 26
        plot_w = self.width - left - 8
        plot_h = self.chart_height - bottom - 16
        top = bottom + plot_h

        canvas.setStrokeColor(LINE)
        canvas.setFillColor(colors.HexColor('#F4F7FA'))
        canvas.rect(left, bottom, plot_w, plot_h, stroke=1, fill=1)

        # Banda del rango promedio ya definido en el informe (decatipos 4 a 7).
        y4 = bottom + (4 - 1) / 9 * plot_h
        y7 = bottom + (7 - 1) / 9 * plot_h
        canvas.setFillColor(colors.Color(0.12, 0.31, 0.47, alpha=0.08))
        canvas.rect(left, y4, plot_w, y7 - y4, stroke=0, fill=1)

        canvas.setStrokeColor(colors.HexColor('#D5DEE7'))
        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 7)
        for score in range(1, 11):
            y = bottom + (score - 1) / 9 * plot_h
            canvas.setStrokeColor(colors.HexColor('#D5DEE7'))
            canvas.line(left, y, left + plot_w, y)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(left - 4, y - 2, str(score))

        count = len(self.labels)
        step = plot_w / max(count - 1, 1)
        points = []
        canvas.setFont('Helvetica', 7)
        for index, (label, value) in enumerate(zip(self.labels, self.values)):
            x = left + index * step
            canvas.setStrokeColor(colors.HexColor('#E3EAF1'))
            canvas.line(x, bottom, x, top)
            canvas.setFillColor(NAVY)
            canvas.drawCentredString(x, 8, label)
            number = _as_float(value)
            if number is None:
                points.append(None)
                continue
            y = bottom + (number - 1) / 9 * plot_h
            points.append((x, y, number))

        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(1.3)
        segment = []
        for point in points + [None]:
            if point is None:
                if len(segment) >= 2:
                    path = canvas.beginPath()
                    path.moveTo(segment[0][0], segment[0][1])
                    for x, y, _number in segment[1:]:
                        path.lineTo(x, y)
                    canvas.drawPath(path, stroke=1, fill=0)
                segment = []
            else:
                segment.append(point)
        points = [point for point in points if point]

        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica', 6)
        for x, y, number in points:
            canvas.setFillColor(colors.white)
            canvas.setStrokeColor(NAVY)
            canvas.circle(x, y, 3.2, stroke=1, fill=1)
            canvas.setFillColor(NAVY)
            canvas.drawCentredString(x, y + 5, _format_number(number))

        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(left, self.chart_height - 10, 'Decatipo')


def _as_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value):
    if value is None:
        return 'No disponible'
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return f'{number:.2f}'.rstrip('0').rstrip('.')


def _data_table(headers, rows, col_widths):
    styles = _styles()
    header = [Paragraph(escape(text), styles['header_cell']) for text in headers]
    data = [header] + rows
    table = Table(data, colWidths=col_widths, repeatRows=1)
    commands = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.3, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for index in range(1, len(data)):
        if index % 2 == 0:
            commands.append(('BACKGROUND', (0, index), (-1, index), ROW_ALT))
    table.setStyle(TableStyle(commands))
    return table


def _paragraph_rows(raw_rows):
    styles = _styles()
    return [[Paragraph(_text(cell), styles['cell']) for cell in row] for row in raw_rows]


def _page_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.5)
    canvas.line(LEFT_MARGIN, PAGE_HEIGHT - 12 * mm, PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - 12 * mm)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(LEFT_MARGIN, 12 * mm, PAGE_WIDTH - RIGHT_MARGIN, 12 * mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT_MARGIN, 8 * mm, 'Informe descriptivo HSPQ')
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 8 * mm, f'Página {doc.page}')
    canvas.restoreState()


def generate_hspq_pdf(report_data):
    """Genera el PDF del informe HSPQ a partir de build_hspq_report(). Devuelve bytes."""
    report = report_data or {}
    student = report.get('estudiante') or {}
    test = report.get('test') or {}
    styles = _styles()
    full_name = ' '.join(
        part for part in (student.get('nombre'), student.get('apellido')) if part
    ) or 'No disponible'

    story = [
        Paragraph('INFORME DE RESULTADOS HSPQ', styles['title']),
        Paragraph('Documento descriptivo para uso del psicólogo', styles['subtitle']),
        _section(styles, '1. Identificación del estudiante'),
        _kv_table([
            ('Nombre', full_name),
            ('CI', student.get('ci_username')),
            ('Edad', student.get('edad')),
            ('Sexo', student.get('sexo')),
            ('Colegio', student.get('colegio')),
            ('Grado escolar', student.get('grado_escolar')),
        ]),
        _section(styles, '2. Identificación del test'),
        _kv_table([
            ('Test', test.get('nombre') or 'HSPQ'),
            ('ID del test', test.get('id_test')),
            ('Total de respuestas', test.get('total_respuestas')),
            ('Completitud', _completitud_text(test.get('completitud') or [])),
        ]),
        _section(styles, '3. Perfil gráfico'),
        Paragraph(
            'Decatipos de las 13 escalas de personalidad. El factor B no forma parte de este perfil '
            'y se informa en la tabla de factores primarios.',
            styles['small'],
        ),
        Spacer(1, 4),
        HspqProfileChart(report.get('perfil_grafico') or []),
        Spacer(1, 6),
        _section(styles, '4. Factores primarios'),
    ]

    primary_rows = _paragraph_rows([
        [
            item.get('factor'),
            _format_number(item.get('puntuacion_directa')) if item.get('puntuacion_directa') is not None else None,
            _format_number(item.get('decatipo')) if item.get('decatipo') is not None else None,
            item.get('nivel'),
            item.get('descripcion'),
        ]
        for item in report.get('factores_primarios') or []
    ]) or _paragraph_rows([['No disponible', '', '', '', 'Sin factores primarios en el informe.']])
    story.append(_data_table(
        ['Factor', 'PD', 'Decatipo', 'Nivel', 'Interpretación'],
        primary_rows,
        [16 * mm, 16 * mm, 20 * mm, 22 * mm, CONTENT_WIDTH - 74 * mm],
    ))

    story.append(_section(styles, '5. Factores secundarios'))
    secondary_rows = _paragraph_rows([
        [
            item.get('clave'),
            item.get('nombre'),
            _format_number(item.get('decatipo')) if item.get('decatipo') is not None else None,
            item.get('nivel'),
            item.get('descripcion'),
        ]
        for item in report.get('factores_secundarios') or []
    ]) or _paragraph_rows([['No disponible', '', '', '', 'Sin factores secundarios en el informe.']])
    story.append(_data_table(
        ['Factor', 'Nombre', 'Decatipo', 'Nivel', 'Interpretación'],
        secondary_rows,
        [16 * mm, 42 * mm, 20 * mm, 22 * mm, CONTENT_WIDTH - 100 * mm],
    ))

    story.append(_section(styles, '6. Observaciones'))
    warnings = report.get('advertencias') or []
    if warnings:
        for warning in warnings:
            tipo = warning.get('tipo') or 'advertencia'
            detalle = warning.get('detalle') or ''
            factor = warning.get('factor')
            prefix = f"{tipo} ({factor})" if factor else tipo
            story.append(Paragraph(f'• {_text(prefix)}: {_text(detalle)}', styles['body']))
            story.append(Spacer(1, 2))
    else:
        story.append(Paragraph('No se registraron advertencias.', styles['body']))

    story.extend([
        _section(styles, '7. Nota final'),
        Paragraph(escape(FINAL_NOTE), styles['note']),
    ])

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title='Informe de resultados HSPQ',
        author='Informe HSPQ',
    )
    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return buffer.getvalue()
