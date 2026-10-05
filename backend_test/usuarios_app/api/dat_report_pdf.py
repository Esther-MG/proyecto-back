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

FINAL_NOTE = (
    "Este informe presenta el puntaje directo y el centil de la Plantilla de Baremos escolares. "
    "Debe ser interpretado por un profesional e integrado después con otros antecedentes. "
    "No constituye un diagnóstico ni recomienda opciones vocacionales. "
    "La conversión 1–99 del sistema no se usa como centil."
)


def _text(value):
    if value is None or value == '':
        return 'No disponible'
    return escape(str(value))


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'DatTitle', parent=base['Title'], fontName='Helvetica-Bold',
            fontSize=16, leading=19, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2,
        ),
        'subtitle': ParagraphStyle(
            'DatSubtitle', parent=base['Normal'], fontName='Helvetica',
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=8,
        ),
        'section': ParagraphStyle(
            'DatSection', parent=base['Heading2'], fontName='Helvetica-Bold',
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=6,
        ),
        'small': ParagraphStyle(
            'DatSmall', parent=base['Normal'], fontName='Helvetica',
            fontSize=8, leading=10, textColor=colors.black,
        ),
        'note': ParagraphStyle(
            'DatNote', parent=base['Normal'], fontName='Helvetica-Oblique',
            fontSize=8, leading=11, textColor=colors.black, alignment=TA_JUSTIFY,
        ),
        'header_cell': ParagraphStyle(
            'DatHeaderCell', parent=base['Normal'], fontName='Helvetica-Bold',
            fontSize=8, leading=10, textColor=colors.white,
        ),
        'cell': ParagraphStyle(
            'DatCell', parent=base['Normal'], fontName='Helvetica',
            fontSize=7.5, leading=9.5, textColor=colors.black,
        ),
    }


def _kv_table(rows):
    styles = _styles()
    data = [[Paragraph(f'<b>{escape(label)}</b>', styles['small']),
             Paragraph(_text(value), styles['small'])] for label, value in rows]
    table = Table(data, colWidths=[42 * mm, CONTENT_WIDTH - 42 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), NAVY_SOFT),
        ('GRID', (0, 0), (-1, -1), 0.3, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    return table


def _data_table(headers, rows):
    styles = _styles()
    header = [Paragraph(escape(text), styles['header_cell']) for text in headers]
    data = [header] + rows
    widths = [22 * mm, CONTENT_WIDTH - 82 * mm, 36 * mm, 24 * mm]
    table = Table(data, colWidths=widths, repeatRows=1)
    commands = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('GRID', (0, 0), (-1, -1), 0.3, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
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


class DatCentileChart(Flowable):
    """Perfil de centiles. Mismo trazo que el perfil HSPQ, sin banda interpretativa."""

    def __init__(self, subtests, height=168):
        super().__init__()
        self.labels = [item.get('codigo') or '—' for item in subtests or []]
        self.values = [item.get('centil') for item in subtests or []]
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

        canvas.setFont('Helvetica', 7)
        for score in (1, 25, 50, 75, 99):
            y = bottom + (score - 1) / 98 * plot_h
            canvas.setStrokeColor(colors.HexColor('#D5DEE7'))
            canvas.line(left, y, left + plot_w, y)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(left - 4, y - 2, str(score))

        count = max(len(self.labels), 1)
        step = plot_w / max(count - 1, 1)
        points = []
        for index, (label, value) in enumerate(zip(self.labels, self.values)):
            x = left + (index * step if count > 1 else plot_w / 2)
            canvas.setStrokeColor(colors.HexColor('#E3EAF1'))
            canvas.line(x, bottom, x, top)
            canvas.setFillColor(NAVY)
            canvas.setFont('Helvetica', 7)
            canvas.drawCentredString(x, 8, str(label))
            if not isinstance(value, (int, float)):
                points.append(None)
                continue
            y = bottom + (float(value) - 1) / 98 * plot_h
            points.append((x, y, value))

        canvas.setStrokeColor(NAVY)
        canvas.setLineWidth(1.3)
        segment = []
        for point in points + [None]:
            if point is None:
                if len(segment) >= 2:
                    path = canvas.beginPath()
                    path.moveTo(segment[0][0], segment[0][1])
                    for x, y, _value in segment[1:]:
                        path.lineTo(x, y)
                    canvas.drawPath(path, stroke=1, fill=0)
                segment = []
            else:
                segment.append(point)

        canvas.setFont('Helvetica', 6)
        for x, y, value in (point for point in points if point):
            canvas.setFillColor(colors.white)
            canvas.setStrokeColor(NAVY)
            canvas.circle(x, y, 3.2, stroke=1, fill=1)
            canvas.setFillColor(NAVY)
            canvas.drawCentredString(x, y + 5, str(int(value)))

        canvas.setFillColor(MUTED)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(left, self.chart_height - 10, 'Centil')


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
    canvas.drawString(LEFT_MARGIN, 8 * mm, 'Informe descriptivo DAT')
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 8 * mm, f'Página {doc.page}')
    canvas.restoreState()


def generate_dat_pdf(report_data):
    """Genera el PDF del informe DAT. Devuelve bytes."""
    report = report_data or {}
    student = report.get('estudiante') or {}
    test = report.get('test') or {}
    profile = report.get('perfil') or {}
    styles = _styles()
    full_name = ' '.join(
        part for part in (student.get('nombre'), student.get('apellido')) if part
    ) or 'No disponible'
    subtests = report.get('subtests') or []

    rows = [[
        Paragraph(_text(item.get('codigo')), styles['cell']),
        Paragraph(_text(item.get('nombre')), styles['cell']),
        Paragraph(_text(item.get('puntaje_directo')), styles['cell']),
        Paragraph(_text(item.get('centil')), styles['cell']),
    ] for item in subtests]
    if not rows:
        rows = [[Paragraph('No disponible', styles['cell'])] * 4]

    notes = '<br/>'.join(_text(note) for note in (report.get('notas') or []) if note)
    warnings = report.get('advertencias') or []
    warning_text = 'No se registraron advertencias.' if not warnings else '<br/>'.join(
        _text(item.get('detalle')) for item in warnings
    )

    story = [
        Paragraph('INFORME DE RESULTADOS DAT', styles['title']),
        Paragraph('Documento descriptivo para uso del psicólogo', styles['subtitle']),
        Paragraph('1. Identificación del estudiante', styles['section']),
        _kv_table([
            ('Nombre', full_name),
            ('CI', student.get('ci_username')),
            ('Edad', student.get('edad')),
            ('Sexo', student.get('sexo')),
            ('Colegio', student.get('colegio')),
            ('Grado escolar', student.get('grado_escolar')),
        ]),
        Paragraph('2. Identificación de la evaluación', styles['section']),
        _kv_table([
            ('Test', test.get('nombre') or 'Test de Aptitudes Diferenciales (DAT)'),
            ('Baremo', test.get('baremo')),
            ('Fecha de aplicación', 'No consta en los datos del test'),
        ]),
        Paragraph('3. Resultados', styles['section']),
        _data_table(
            ['Código', 'Subtest', 'Puntaje directo', 'Centil'],
            rows,
        ),
        Paragraph('4. Perfil de centiles', styles['section']),
        Paragraph(
            'Cada punto es el centil de la Plantilla de Baremos escolares. No es la conversión 1–99 del sistema.',
            styles['small'],
        ),
        Spacer(1, 4),
        DatCentileChart(subtests),
        Paragraph('5. Interpretación descriptiva del perfil', styles['section']),
        Paragraph(_text(profile.get('interpretacion')), styles['small']),
        Paragraph('6. Fortalezas relativas', styles['section']),
        Paragraph(_text(profile.get('fortalezas')), styles['small']),
        Paragraph('7. Áreas de menor desempeño relativo', styles['section']),
        Paragraph(_text(profile.get('areas_menores')), styles['small']),
        Paragraph('8. Síntesis', styles['section']),
        Paragraph(_text(profile.get('sintesis')), styles['small']),
        Paragraph('9. Lectura del perfil DAT', styles['section']),
        Paragraph(_text(profile.get('lectura')), styles['small']),
        Paragraph('10. Consideraciones profesionales', styles['section']),
        Paragraph(FINAL_NOTE, styles['note']),
        Spacer(1, 4),
        Paragraph(notes or 'No disponible', styles['note']),
        Spacer(1, 4),
        Paragraph(warning_text, styles['small']),
    ]

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title='Informe de resultados DAT',
        author='Informe DAT',
    )
    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return buffer.getvalue()
