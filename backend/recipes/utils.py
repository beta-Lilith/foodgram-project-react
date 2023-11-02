import io
from datetime import datetime

from reportlab.pdfgen import canvas

from foodgram_project.settings import (BIG_FONT, BIG_FONT_SIZE, FILEFORMAT,
                                       SMALL_FONT, SMALL_FONT_SIZE)

START = 0
COLUMN_0 = 70
LINE_0 = 750
LINE_1 = 730
LINE_2 = 710
LINE_3 = 690
TEXT_0 = 'Список продуктов:'
TEXT_2 = 'Рецепты:'
NEXT_LINE = 20


def make_doc(ingredients, recipes):
    date = str(datetime.today().date())
    recipes_list = (set(recipe['name'] for recipe in recipes))
    if FILEFORMAT == 'text/plain':
        return (
            '\n'.join((
                TEXT_0,
                date,
                TEXT_2,
                '\n'.join(recipes_list) + '\n',
                '\n'.join(
                    f'{index + 1}. {item["name"]} '
                    f'({item["unit"]}) - {item["amount"]}'
                    for index, item in enumerate(ingredients)))),
            date)
    if FILEFORMAT == 'application/pdf':
        buffer = io.BytesIO()
        doc = canvas.Canvas(buffer)
        doc.setFont(BIG_FONT, BIG_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_0, TEXT_0)
        doc.setFont(SMALL_FONT, SMALL_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_1, date)
        doc.drawString(COLUMN_0, LINE_2, TEXT_2)
        y = LINE_3
        for recipe in recipes_list:
            doc.drawString(COLUMN_0, y, recipe)
            y -= NEXT_LINE
        y -= NEXT_LINE
        numeration = 1
        for item in ingredients:
            doc.drawString(
                COLUMN_0, y,
                f'{numeration}. {item["name"]} '
                f'({item["unit"]}) - {item["amount"]}',)
            y -= NEXT_LINE
            numeration += 1
        doc.showPage()
        doc.save()
        buffer.seek(START)
        return buffer, date
