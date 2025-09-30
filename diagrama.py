# diagrama_cap6.py
# Genera un diagrama de 1 página (Carta 8.5x11" @300 DPI) en PNG y PDF
# Contiene: ciencia de datos, ML, tipos (supervisado, no supervisado, refuerzo),
# "minería de datos" engañoso, dataquake, correlaciones espurias,
# abstracción/representación, y aplicaciones/negocios con ML.

from PIL import Image, ImageDraw, ImageFont
from math import atan2, cos, sin

# --- Configuración del lienzo (Carta a 300 DPI) ---
W, H = 2550, 3300  # px
MARGIN = 100

# --- Utilidades de fuente ---
def load_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
]

# Tamaños pensados para lectura clara en PDF impreso
F_TITLE = load_font(FONT_PATHS, 110)
F_SUB   = load_font(FONT_PATHS, 56)
F_BOX   = load_font(FONT_PATHS, 44)
F_SM    = load_font(FONT_PATHS, 38)

# --- Utilidades de dibujo ---
def rrect(draw, xy, radius=26, outline="black", width=5, fill=None):
    draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width, fill=fill)

def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_text_in_box(draw, text, box, font, fill="black", margin=28, align="center", line_spacing=12):
    x0, y0, x1, y1 = box
    max_w = x1 - x0 - 2*margin
    # Envolver por ancho (por párrafos)
    lines = []
    for para in text.split("\n"):
        para = para.rstrip()
        if not para:
            lines.append("")
        else:
            lines.extend(wrap_text(draw, para, font, max_w))
    # Altura total
    line_h = font.getbbox("Ag")[3] - font.getbbox("Ag")[1]
    total_h = len(lines) * (line_h + line_spacing) - line_spacing
    y = y0 + ((y1 - y0 - total_h) // 2)
    for ln in lines:
        w = draw.textlength(ln, font=font)
        if align == "center":
            x = x0 + ((x1 - x0 - w) // 2)
        elif align == "left":
            x = x0 + margin
        else:  # right
            x = x1 - margin - w
        draw.text((x, y), ln, fill=fill, font=font)
        y += line_h + line_spacing

def arrow(draw, p0, p1, width=8, fill="black", head_len=36, head_w=22):
    x0, y0 = p0; x1, y1 = p1
    draw.line((x0, y0, x1, y1), fill=fill, width=width)
    ang = atan2(y1 - y0, x1 - x0)
    pA = (x1, y1)
    pB = (x1 - head_len*cos(ang) - head_w*sin(ang), y1 - head_len*sin(ang) + head_w*cos(ang))
    pC = (x1 - head_len*cos(ang) + head_w*sin(ang), y1 - head_len*sin(ang) - head_w*cos(ang))
    draw.polygon([pA, pB, pC], fill=fill)

def generar_diagrama(out_png="Cap6_Diagrama_Ciencia_de_Datos_v2.png",
                     out_pdf="Cap6_Diagrama_Ciencia_de_Datos_v2.pdf"):
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)

    # Título y subtítulo
    title = "Que no se nos olvide la ciencia de datos — Cap. 6"
    draw.text(((W - draw.textlength(title, F_TITLE)) // 2, 70), title, font=F_TITLE, fill="black")
    subtitle = "Diagrama de una página con conceptos y conexiones clave"
    draw.text(((W - draw.textlength(subtitle, F_SUB)) // 2, 210), subtitle, font=F_SUB, fill="black")

    # Centro: Ciencia de datos
    center_box = (600, 320, 1950, 620)
    rrect(draw, center_box, fill="#f1f5f9")
    draw_text_in_box(draw,
        "CIENCIA DE DATOS\nCiclo: obtener → preparar → modelar → evaluar → desplegar → comunicar",
        center_box, F_BOX
    )

    # Pipeline
    pipeline_y = 760
    step_w, step_h, gap = 380, 180, 34
    steps = ["Datos", "Limpieza", "Ingeniería/Modelado", "Evaluación", "Despliegue", "Comunicación"]
    boxes_pipeline = []
    start_x = (W - (len(steps) * step_w + (len(steps) - 1) * gap)) // 2
    for i, label in enumerate(steps):
        x0 = start_x + i * (step_w + gap); y0 = pipeline_y
        box = (x0, y0, x0 + step_w, y0 + step_h)
        rrect(draw, box, fill="#eef2ff")
        draw_text_in_box(draw, label, box, F_BOX)
        boxes_pipeline.append(box)
        if i < len(steps) - 1:
            arrow(draw, (x0 + step_w + 8, y0 + step_h // 2), (x0 + step_w + gap - 8, y0 + step_h // 2))

    # ML sobre modelado
    model_box = boxes_pipeline[2]
    mx = (model_box[0] + model_box[2]) // 2
    ml_box = (mx - 360, model_box[1] - 290, mx + 360, model_box[1] - 100)
    rrect(draw, ml_box, fill="#ecfeff")
    draw_text_in_box(draw, "APRENDIZAJE AUTOMÁTICO (ML)\nPatrones estadísticos. Punto de partida: datos.", ml_box, F_SM)
    arrow(draw, ((ml_box[0] + ml_box[2]) // 2, ml_box[3]), (mx, model_box[1] - 8))

    # Tipos de ML (tres cajas)
    types_y = model_box[1] + step_h + 90
    type_w, type_h = 520, 200
    tx_start = mx - (3 * type_w + 2 * gap) // 2
    type_texts = [
        ("Supervisado", "Con etiquetas → predecir y. Ej.: spam; riesgo."),
        ("No supervisado", "Sin etiquetas → descubrir estructura (clusters)."),
        ("Refuerzo", "Agente + recompensa/castigo → aprende por iteración."),
    ]
    type_boxes = []
    for i, (t, d) in enumerate(type_texts):
        x0 = tx_start + i * (type_w + gap)
        box = (x0, types_y, x0 + type_w, types_y + type_h)
        rrect(draw, box, fill="#f0fdf4")
        draw_text_in_box(draw, f"{t}\n{d}", box, F_SM)
        type_boxes.append(box)
        arrow(draw, (((model_box[0] + model_box[2]) // 2), model_box[1] + step_h + 10),
              (((box[0] + box[2]) // 2), box[1] - 10))

    # “Minería de datos” engañoso (post-it)
    md_box = (130, 380, 760, 590)
    rrect(draw, md_box, fill="#fff7ed")
    draw_text_in_box(draw, "“Minería de datos” es engañoso:\nextrae **patrones**, no datos.", md_box, F_SM, align="left")
    arrow(draw, (((md_box[0] + md_box[2]) // 2), md_box[3]), (boxes_pipeline[0][0] + step_w // 2, boxes_pipeline[0][1] - 10))

    # Dataquake
    dq_box = (W - 760, 380, W - 130, 650)
    rrect(draw, dq_box, fill="#fef2f2")
    draw_text_in_box(draw, "DATAQUAKE: más datos + cómputo + nube/redes sociales\n⇒ reconfigura sectores.",
                     dq_box, F_SM, align="left")
    arrow(draw, (((dq_box[0] + dq_box[2]) // 2), dq_box[3]), (((center_box[0] + center_box[2]) // 2), center_box[1]))

    # Correlaciones espurias
    esp_box = (130, 2100, 1180, 2450)
    rrect(draw, esp_box, fill="#fff1f2")
    draw_text_in_box(draw,
                     "⚠ Correlaciones espurias:\nCorrelación ≠ causalidad (tercer factor oculto).\n"
                     "Ej.: divorcios (Maine) ~ margarina; mozzarella ~ PhD ing. civil.",
                     esp_box, F_SM, align="left")
    arrow(draw, (esp_box[2], (esp_box[1] + esp_box[3]) // 2),
          (boxes_pipeline[3][0], boxes_pipeline[3][1] + step_h // 2))

    # Abstracción / Representación
    abs_box = (W - 1180, 2100, W - 130, 2500)
    rrect(draw, abs_box, fill="#f0f9ff")
    draw_text_in_box(draw,
                     "Abstracción ≠ neutral (mapa ≠ territorio).\n"
                     "Elecciones humanas: datos, algoritmo, métricas.\n"
                     "¿Representatividad? ¿sesgos?",
                     abs_box, F_SM, align="left")
    arrow(draw, (abs_box[0], (abs_box[1] + abs_box[3]) // 2),
          (boxes_pipeline[2][2], boxes_pipeline[2][1] + step_h // 2))

    # Aplicaciones (dos columnas)
    apps_title = "Aplicaciones y negocios impulsados por ML"
    draw.text(((W - draw.textlength(apps_title, F_BOX)) // 2, 2580), apps_title, font=F_BOX, fill="black")

    col1 = [
        "Publicidad/segmentación (plataformas)",
        "Recomendación (retail/streaming)",
        "Fraude y crédito (finanzas)",
        "Movilidad/visión (autonomía, IoT)",
    ]
    col2 = [
        "Diagnóstico por imagen (salud)",
        "Noticias automatizadas (medios)",
        "Asistentes/robots conectados (hogar)",
        "Sensores y mantenimiento predictivo",
    ]

    y_start = 2660
    line_h = F_SM.getbbox("Ag")[3] - F_SM.getbbox("Ag")[1] + 18
    x_left = 250
    x_right = W // 2 + 100
    for i, txt in enumerate(col1):
        draw.text((x_left, y_start + i * line_h), "• " + txt, font=F_SM, fill="black")
    for i, txt in enumerate(col2):
        draw.text((x_right, y_start + i * line_h), "• " + txt, font=F_SM, fill="black")

    # Notas breves (una línea)
    notes = "ML es estadístico (Boden). Los datos son el inicio (Alpaydin). Correlación ≠ causalidad (Vigen)."
    draw.text(((W - draw.textlength(notes, F_SM)) // 2, 3000), notes, font=F_SM, fill="black")

    # Guardar
    img.save(out_png, "PNG")
    img.save(out_pdf, "PDF", resolution=300)
    print(f"Archivos generados:\n- {out_png}\n- {out_pdf}")

if __name__ == "__main__":
    generar_diagrama()
