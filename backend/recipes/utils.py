import io
from datetime import datetime

from reportlab.pdfgen import canvas

from foodgram_project.settings import (BIG_FONT, BIG_FONT_SIZE, FILEFORMAT,
                                       SMALL_FONT, SMALL_FONT_SIZE)

START = 0
COLUMN_0 = 70
COLUMN_1 = 300
LINE_0 = 750
LINE_1 = 730
LINE_2 = 710
LINE_3 = 660
TEXT_0 = 'Список ингредиентов:'
TEXT_2 = 'Рецепты: '
NEXT_LINE = 20


def make_doc(ingredients, recipes):
    date = str(datetime.today().date())
    recipes_list = ''.join((
        TEXT_2,
        ', '.join(set(
            recipe['name']
            for recipe in recipes))))
    if FILEFORMAT == 'text/plain':
        return (
            '\n'.join((
                TEXT_0,
                date,
                recipes_list,
                '\n'.join(
                    f'{index + 1}. {item["name"]}: '
                    f'{item["amount"]} {item["unit"]}'
                    for index, item in enumerate(ingredients)))),
            date)
    if FILEFORMAT == 'application/pdf':
        buffer = io.BytesIO()
        doc = canvas.Canvas(buffer)
        doc.setFont(BIG_FONT, BIG_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_0, TEXT_0)
        doc.setFont(SMALL_FONT, SMALL_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_1, date)
        doc.drawString(COLUMN_0, LINE_2, recipes_list)
        y = LINE_3
        numeration = 1
        for item in ingredients:
            doc.drawString(COLUMN_0, y, f'{numeration}. {item["name"]}',)
            doc.drawString(
                COLUMN_1, y, f'{item["amount"]} {item["unit"]}',)
            y -= NEXT_LINE
            numeration += 1
        doc.showPage()
        doc.save()
        buffer.seek(START)
        return buffer, date
