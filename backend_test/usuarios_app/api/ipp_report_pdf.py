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
PR_COLOR = MUTED

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 16 * mm
RIGHT_MARGIN = 16 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

FINAL_NOTE = (
    "Este informe presenta el puntaje directo y la puntuación transformada del sistema. "
    "Esa conversión no está verificada contra el baremo del IPP original, así que no se presenta "
    "como percentil ni se traduce a niveles cualitativos. Debe interpretarlo un profesional. "
    "No constituye un diagnóstico, no afirma una capacidad y no recomienda opciones vocacionales."
)


def _text(value):
    if value is None or value == '':
        return 'No disponible'
    return escape(str(value))


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'IppTitle', parent=base['Title'], fontName='Helvetica-Bold',
            fontSize=16, leading=19, textColor=NAVY, alignment=TA_LEFT, spaceAfter=2,
        ),
        'subtitle': ParagraphStyle(
            'IppSubtitle', parent=base['Normal'], fontName='Helvetica',
            fontSize=9, leading=12, textColor=MUTED, spaceAfter=8,
        ),
        'section': ParagraphStyle(
            'IppSection', parent=base['Heading2'], fontName='Helvetica-Bold',
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=10, spaceAfter=6,
        ),
        'small': ParagraphStyle(
            'IppSmall', parent=base['Normal'], fontName='Helvetica',
            fontSize=8, leading=10, textColor=colors.black,
        ),
        'note': ParagraphStyle(
            'IppNote', parent=base['Normal'], fontName='Helvetica-Oblique',
            fontSize=8, leading=11, textColor=colors.black, alignment=TA_JUSTIFY,
        ),
        'header_cell': ParagraphStyle(
            'IppHeaderCell', parent=base['Normal'], fontName='Helvetica-Bold',
            fontSize=8, leading=10, textColor=colors.white,
        ),
        'cell': ParagraphStyle(
            'IppCell', parent=base['Normal'], fontName='Helvetica',
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
    widths = [CONTENT_WIDTH - 108 * mm, 27 * mm, 27 * mm, 27 * mm, 27 * mm]
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


class IppProfileChart(Flowable):
    """Perfil AC/PR. Mismo trazo que HSPQ/DAT, con dos series."""

    def __init__(self, fields, height=214):
        super().__init__()
        self.labels = [str(item.get('id')) for item in fields or []]
        self.ac = [item.get('pt_ac') for item in fields or []]
        self.pr = [item.get('pt_pr') for item in fields or []]
        self.chart_height = height

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        return availWidth, self.chart_height

    def _y(self, value, bottom, plot_h):
        return bottom + (float(value) - 1) / 98 * plot_h

    def _series(self, canvas, xs, values, bottom, plot_h, color):
        points = []
        for x, value in zip(xs, values):
            if not isinstance(value, (int, float)):
                points.append(None)
                continue
            points.append((x, self._y(value, bottom, plot_h), value))
        canvas.setStrokeColor(color)
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
        return [point for point in points if point]

    def draw(self):
        canvas = self.canv
        left = 28
        bottom = 28
        plot_w = self.width - left - 8
        plot_h = self.chart_height - bottom - 22
        top = bottom + plot_h

        canvas.setStrokeColor(LINE)
        canvas.setFillColor(colors.HexColor('#F4F7FA'))
        canvas.rect(left, bottom, plot_w, plot_h, stroke=1, fill=1)

        canvas.setFont('Helvetica', 7)
        for score in (1, 25, 50, 75, 99):
            y = self._y(score, bottom, plot_h)
            canvas.setStrokeColor(colors.HexColor('#D5DEE7'))
            canvas.line(left, y, left + plot_w, y)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(left - 4, y - 2, str(score))

        count = max(len(self.labels), 1)
        step = plot_w / max(count - 1, 1)
        xs = []
        for index, label in enumerate(self.labels):
            x = left + (index * step if count > 1 else plot_w / 2)
            xs.append(x)
            canvas.setStrokeColor(colors.HexColor('#E3EAF1'))
            canvas.line(x, bottom, x, top)
            canvas.setFillColor(NAVY)
            canvas.setFont('Helvetica', 7)
            canvas.drawCentredString(x, 10, label)

        ac_points = self._series(canvas, xs, self.ac, bottom, plot_h, NAVY)
        pr_points = self._series(canvas, xs, self.pr, bottom, plot_h, PR_COLOR)
        for points, color, dy in ((ac_points, NAVY, 5), (pr_points, PR_COLOR, -9)):
            canvas.setFont('Helvetica', 6)
            for x, y, value in points:
                canvas.setFillColor(colors.white)
                canvas.setStrokeColor(color)
                canvas.circle(x, y, 2.6, stroke=1, fill=1)
                canvas.setFillColor(color)
                canvas.drawCentredString(x, y + dy, str(int(value)))

        canvas.setFillColor(NAVY)
        canvas.setFont('Helvetica', 7)
        canvas.drawString(left, self.chart_height - 10, 'AC actividades')
        canvas.setFillColor(PR_COLOR)
        canvas.drawString(left + 78, self.chart_height - 10, 'PR profesiones')
        canvas.setFillColor(MUTED)
        canvas.drawRightString(left + plot_w, self.chart_height - 10, 'Puntuación transformada')


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
    canvas.drawString(LEFT_MARGIN, 8 * mm, 'Informe descriptivo IPP')
    canvas.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, 8 * mm, f'Página {doc.page}')
    canvas.restoreState()


def generate_ipp_pdf(report_data):
    """Genera el PDF del informe IPP. Devuelve bytes."""
    report = report_data or {}
    student = report.get('estudiante') or {}
    test = report.get('test') or {}
    profile = report.get('perfil') or {}
    styles = _styles()
    full_name = ' '.join(
        part for part in (student.get('nombre'), student.get('apellido')) if part
    ) or 'No disponible'
    fields = report.get('campos') or []
    rows = [[
        Paragraph(f"{item.get('id')}. {_text(item.get('nombre'))}", styles['cell']),
        Paragraph(_text(item.get('pd_ac')), styles['cell']),
        Paragraph(_text(item.get('pd_pr')), styles['cell']),
        Paragraph(_text(item.get('pt_ac')), styles['cell']),
        Paragraph(_text(item.get('pt_pr')), styles['cell']),
    ] for item in fields]
    if not rows:
        rows = [[Paragraph('No disponible', styles['cell'])] * 5]

    notes = '<br/>'.join(_text(note) for note in (report.get('notas') or []) if note)
    warnings = report.get('advertencias') or []
    warning_text = 'No se registraron advertencias.' if not warnings else '<br/>'.join(
        _text(item.get('detalle')) for item in warnings
    )
    story = [
        Paragraph('INFORME DE RESULTADOS IPP', styles['title']),
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
        Paragraph('2. Identificación del IPP', styles['section']),
        _kv_table([
            ('Test', test.get('nombre')),
            ('Instrumento', 'IPP original, 17 campos profesionales'),
            ('Ítems', test.get('items')),
            ('Actividades (AC)', 'Preferencia por actividades'),
            ('Profesiones (PR)', 'Preferencia por profesiones'),
            ('Escala transformada', test.get('escala')),
            ('Fecha de aplicación', 'No consta en los datos del test'),
        ]),
        Paragraph('3. Resultados', styles['section']),
        Paragraph(
            'PD: puntaje directo. Transf.: puntuación transformada del sistema. No es un percentil verificado.',
            styles['small'],
        ),
        Spacer(1, 4),
        _data_table(
            ['Campo', 'PD AC', 'PD PR', 'Transf. AC', 'Transf. PR'],
            rows,
        ),
        Paragraph('4. Perfil gráfico AC–PR', styles['section']),
        Paragraph(
            'Cada línea compara la puntuación transformada de actividades y profesiones en los 17 campos. '
            'No es un percentil ni un nivel del baremo.',
            styles['small'],
        ),
        Spacer(1, 4),
        IppProfileChart(fields),
        Paragraph('5. Interpretación descriptiva del perfil', styles['section']),
        Paragraph(_text(profile.get('interpretacion')), styles['small']),
        Paragraph('6. Intereses relativamente más altos y más bajos', styles['section']),
        Paragraph(_text(profile.get('altos_bajos')), styles['small']),
        Paragraph('7. Relación entre actividades y profesiones', styles['section']),
        Paragraph(_text(profile.get('relacion')), styles['small']),
        Paragraph('8. Síntesis profesional', styles['section']),
        Paragraph(_text(profile.get('sintesis')), styles['small']),
        Paragraph('9. Consideraciones profesionales', styles['section']),
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
        title='Informe de resultados IPP',
        author='Informe IPP',
    )
    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    return buffer.getvalue()
