import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

NAVY = colors.HexColor('#1F4E79')
NAVY_SOFT = colors.HexColor('#E7EEF5')
LINE = colors.HexColor('#C5D0DC')
MUTED = colors.HexColor('#5B6770')

PAGE_WIDTH, PAGE_HEIGHT = LETTER
LEFT_MARGIN = 16 * mm
RIGHT_MARGIN = 16 * mm
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN


def _text(value):
    if value is None or value == '':
        return 'No disponible'
    return escape(str(value))


def _styles():
    base = getSampleStyleSheet()

    return {
        'title': ParagraphStyle(
            'GeneralTitle',
            parent=base['Title'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),

        'subtitle': ParagraphStyle(
            'GeneralSubtitle',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=MUTED,
            spaceAfter=10,
        ),

        'section': ParagraphStyle(
            'GeneralSection',
            parent=base['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
        ),

        'body': ParagraphStyle(
            'GeneralBody',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),

        'note': ParagraphStyle(
            'GeneralNote',
            parent=base['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=MUTED,
            alignment=TA_JUSTIFY,
        ),

        'label': ParagraphStyle(
            'GeneralLabel',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=NAVY,
        ),

        'value': ParagraphStyle(
            'GeneralValue',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.black,
        ),
    }


def _student_table(student):
    styles = _styles()

    full_name = ' '.join(
        part for part in (
            student.get('nombre'),
            student.get('apellido'),
        ) if part
    ) or 'No disponible'

    rows = [
        ('Nombre', full_name),
        ('CI', student.get('ci_username')),
        ('Edad', student.get('edad')),
        ('Sexo', student.get('sexo')),
        ('Colegio', student.get('colegio')),
        ('Grado escolar', student.get('grado_escolar')),
    ]

    data = [
        [
            Paragraph(f'<b>{escape(label)}</b>', styles['value']),
            Paragraph(_text(value), styles['value']),
        ]
        for label, value in rows
    ]

    table = Table(
        data,
        colWidths=[42 * mm, CONTENT_WIDTH - 42 * mm],
    )

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), NAVY_SOFT),
        ('GRID', (0, 0), (-1, -1), 0.3, LINE),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    return table


def _page_footer(canvas, doc):
    canvas.saveState()

    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.5)
    canvas.line(
        LEFT_MARGIN,
        PAGE_HEIGHT - 12 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        PAGE_HEIGHT - 12 * mm,
    )

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(
        LEFT_MARGIN,
        12 * mm,
        PAGE_WIDTH - RIGHT_MARGIN,
        12 * mm,
    )

    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)

    canvas.drawString(
        LEFT_MARGIN,
        8 * mm,
        'Informe de resultados de orientación vocacional',
    )

    canvas.drawRightString(
        PAGE_WIDTH - RIGHT_MARGIN,
        8 * mm,
        f'Página {doc.page}',
    )

    canvas.restoreState()


def _paragraphs(texts, style):
    bloques = texts if isinstance(texts, (list, tuple)) else [texts]
    return [
        Paragraph(_text(texto), style)
        for texto in bloques
        if texto
    ]


def generate_general_pdf(report_data):
    """Genera el informe general destinado al estudiante."""

    report = report_data or {}
    student = report.get('estudiante') or {}
    interpretation = report.get('interpretacion_general') or {}
    styles = _styles()
    nombre = interpretation.get('nombre') or student.get('nombre') or 'Estudiante'

    story = [
        Paragraph('INFORME DE RESULTADOS', styles['title']),
        Paragraph(f'Resultados de {nombre}', styles['subtitle']),
        Paragraph('1. Datos del estudiante', styles['section']),
        _student_table(student),
        Spacer(1, 6),
        Paragraph('2. Cómo leer tus resultados', styles['section']),
        Paragraph(_text(interpretation.get('introduccion')), styles['body']),
        Paragraph('3. Tus aptitudes', styles['section']),
        *_paragraphs(interpretation.get('aptitudes') or interpretation.get('dat'), styles['body']),
        Paragraph('4. Tus intereses', styles['section']),
        *_paragraphs(interpretation.get('intereses') or interpretation.get('ipp'), styles['body']),
        Paragraph('5. Cómo te describe el cuestionario', styles['section']),
        *_paragraphs(interpretation.get('personalidad') or interpretation.get('hspq'), styles['body']),
        Paragraph('6. Lectura conjunta', styles['section']),
        *_paragraphs(interpretation.get('conjunto') or interpretation.get('resumen_general'), styles['body']),
        Spacer(1, 8),
        Paragraph('Ten en cuenta', styles['section']),
        Paragraph(_text(interpretation.get('conclusion')), styles['note']),
    ]

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title='Informe de resultados de orientación vocacional',
        author='Sistema de Orientación Vocacional',
    )

    document.build(
        story,
        onFirstPage=_page_footer,
        onLaterPages=_page_footer,
    )

    return buffer.getvalue()