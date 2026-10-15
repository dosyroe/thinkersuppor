from pathlib import Path
import re
import subprocess
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT = Path(r"D:\DemoExam")
PROJECT = ROOT / "exam_project"
FONT = Path(r"C:\Users\arcen\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\share\fonts\DejaVuSans.ttf")
pdfmetrics.registerFont(TTFont("DiagramFont", str(FONT)))
path = PROJECT / "ERD_module_1.pdf"
diagram = canvas.Canvas(str(path), pagesize=landscape(A4))
page_w, page_h = landscape(A4)
diagram.setTitle("Чудо Обувь - ERD базы PostgreSQL")
diagram.setAuthor("Чудо Обувь")

schema = (PROJECT / "database/schema.sql").read_text(encoding="utf-8")
tables = {}
for name, body in re.findall(r"CREATE TABLE public\.(\w+) \((.*?)\n\);", schema, flags=re.S):
    columns = []
    for line in body.splitlines():
        match = re.match(r"\s*([a-z_]+)\s+([A-Z]+(?:\([0-9, ]+\))?)(.*)", line)
        if match:
            col, kind, rest = match.groups()
            flags = []
            if "PRIMARY KEY" in rest:
                flags.append("PK")
            if "REFERENCES" in rest:
                flags.append("FK")
            if "UNIQUE" in rest:
                flags.append("U")
            columns.append((col, kind, "/".join(flags)))
    tables[name] = columns
assert len(tables) == 7

diagram.setFillColor(colors.HexColor("#233D3B"))
diagram.setFont("DiagramFont", 17)
diagram.drawString(30, page_h - 33, "Чудо Обувь: схема базы данных")
diagram.setFont("DiagramFont", 8.5)
diagram.setFillColor(colors.HexColor("#526B68"))
diagram.drawString(30, page_h - 51, "PostgreSQL / 7 таблиц / все связи 1:M / схема соответствует database/schema.sql")

positions = {"roles": (30, 515), "users": (311, 515), "orders": (592, 515),
             "products": (30, 355), "stock_items": (311, 355), "order_items": (592, 355),
             "sizes": (30, 155)}
notes = {"roles": "U: role_code, role_name", "users": "U: login", "orders": "Клиент и дата заказа",
         "products": "U: product_name + manufacturer", "sizes": "U: size_value; >0",
         "stock_items": "U: product_id + size_id; остаток >=0",
         "order_items": "U: order_id + stock_item_id; пар >0"}
row_y = {}
width = 220
for name, (x, top) in positions.items():
    rows = tables[name]
    height = 31 + len(rows) * 15 + 22
    bottom = top - height
    diagram.setStrokeColor(colors.HexColor("#AAC7C2"))
    diagram.setFillColor(colors.white)
    diagram.roundRect(x, bottom, width, height, 5, fill=1, stroke=1)
    diagram.setFillColor(colors.HexColor("#D2F6E7"))
    diagram.rect(x + 1, top - 26, width - 2, 25, fill=1, stroke=0)
    diagram.setFillColor(colors.HexColor("#233D3B"))
    diagram.setFont("DiagramFont", 11)
    diagram.drawString(x + 10, top - 18, name)
    for index, (column, kind, flags) in enumerate(rows):
        y = top - 41 - index * 15
        row_y[(name, column)] = y + 3
        diagram.setFont("DiagramFont", 7.5)
        diagram.setFillColor(colors.HexColor("#527C75"))
        diagram.drawString(x + 8, y, flags)
        diagram.setFillColor(colors.HexColor("#263F3B"))
        diagram.drawString(x + 28, y, column)
        diagram.setFillColor(colors.HexColor("#667874"))
        diagram.setFont("DiagramFont", 6.9)
        diagram.drawRightString(x + width - 8, y, kind)
    diagram.setStrokeColor(colors.HexColor("#DDE9E6"))
    diagram.line(x + 8, bottom + 21, x + width - 8, bottom + 21)
    diagram.setFont("DiagramFont", 6.6)
    diagram.setFillColor(colors.HexColor("#667874"))
    diagram.drawString(x + 8, bottom + 9, notes[name])


def arrow(points, right=True):
    diagram.setStrokeColor(colors.HexColor("#568F86"))
    diagram.setFillColor(colors.HexColor("#568F86"))
    diagram.setLineWidth(1.1)
    for first, second in zip(points, points[1:]):
        diagram.line(*first, *second)
    x, y = points[-1]
    delta = -5 if right else 5
    p = diagram.beginPath()
    p.moveTo(x, y)
    p.lineTo(x + delta, y + 3)
    p.lineTo(x + delta, y - 3)
    p.close()
    diagram.drawPath(p, stroke=0, fill=1)
    diagram.setFont("DiagramFont", 8)
    diagram.drawString(points[0][0] + (3 if right else -8), points[0][1] + 5, "1")
    diagram.drawString(points[-1][0] + (-12 if right else 3), points[-1][1] + 5, "M")


def across(source, source_column, target, target_column, bend):
    sx = positions[source][0] + width
    tx = positions[target][0]
    sy = row_y[(source, source_column)]
    ty = row_y[(target, target_column)]
    arrow([(sx, sy), (bend, sy), (bend, ty), (tx, ty)])


across("roles", "role_id", "users", "role_id", 279)
across("users", "user_id", "orders", "user_id", 563)
across("products", "product_id", "stock_items", "product_id", 281)
across("sizes", "size_id", "stock_items", "size_id", 265)
across("stock_items", "stock_item_id", "order_items", "stock_item_id", 564)
sx = positions["orders"][0] + width
sy = row_y[("orders", "order_id")]
ty = row_y[("order_items", "order_id")]
arrow([(sx, sy), (828, sy), (828, ty), (sx, ty)], right=False)

diagram.setFont("DiagramFont", 8)
diagram.setFillColor(colors.HexColor("#526B68"))
diagram.drawString(311, 165, "PK - первичный ключ; FK - внешний ключ; U - уникальность.")
diagram.drawString(311, 148, "Стрелка: первичный ключ (1) -> внешний ключ (M).")
diagram.drawString(311, 131, "Удаление orders каскадно удаляет order_items.")
diagram.drawString(311, 114, "products.price - базовая цена; order_items.unit_price - цена покупки.")
diagram.drawString(311, 97, "Остаток хранится для конкретной модели и размера.")
diagram.setStrokeColor(colors.HexColor("#DDE9E6"))
diagram.line(30, 46, page_w - 30, 46)
diagram.setFont("DiagramFont", 7.5)
diagram.drawString(30, 30, "Все обязательные значения заданы NOT NULL; image_path допускает отсутствие изображения.")
diagram.drawRightString(page_w - 30, 30, "1 / 1")
diagram.save()

reader = PdfReader(path)
text = reader.pages[0].extract_text()
assert len(reader.pages) == 1 and all(name in text for name in tables)
output = ROOT / "analysis/tmp/pdfs"
output.mkdir(parents=True, exist_ok=True)
subprocess.run([r"C:\Users\arcen\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe", "-png", "-r", "130", "-singlefile", str(path), str(output / "exam_erd")], check=True)
print("ERD created, seven tables verified and rendered:", path)
