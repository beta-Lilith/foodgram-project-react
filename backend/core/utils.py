from reportlab.pdfgen import canvas

from foodgram_project.settings import (BIG_FONT, BIG_FONT_SIZE, COLUMN_0,
                                       COLUMN_1, LINE_0, LINE_1, LINE_2,
                                       NEXT_LINE, SMALL_FONT, SMALL_FONT_SIZE,
                                       TEXT_0, FILEPATH, FILEFORMAT, DATE)


def make_doc(ingredients):
    if FILEFORMAT == '.pdf':
        doc = canvas.Canvas(FILEPATH)
        doc.setFont(BIG_FONT, BIG_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_0, TEXT_0)
        doc.setFont(SMALL_FONT, SMALL_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_1, str(DATE))
        y = LINE_2
        for item in ingredients:
            doc.drawString(COLUMN_0, y, f'- {item["name"]}',)
            doc.drawString(
                COLUMN_1, y, f'{str(item["amount"])} {item["unit"]}',)
            y -= NEXT_LINE
        doc.showPage()
        doc.save()
    if FILEFORMAT == '.txt':
        doc = []
        doc.append(TEXT_0)
        doc.append(str(DATE))
        for item in ingredients:
            doc.append(
                f'- {item["name"]}: {str(item["amount"])} {item["unit"]}')
        with open(FILEPATH, 'w') as file:
            file.write('\n'.join(doc))
