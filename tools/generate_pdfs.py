"""
Generate the two shareable Free to Build PDFs using ReportLab.

Outputs:
  assets/freetobuild-manifesto.pdf
  assets/freetobuild-press-kit.pdf
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)

# Brand
BG = HexColor("#0a0a0a")
BG2 = HexColor("#161513")
FG = HexColor("#f5f2ea")
FG_DIM = HexColor("#a8a196")
ACCENT = HexColor("#ff5722")
ACCENT_2 = HexColor("#ffb703")
LINE = Color(245/255, 242/255, 234/255, alpha=0.12)
INK = HexColor("#111111")

W, H = A4  # 595.27 x 841.89 pts
MARGIN = 22 * mm


# -------- drawing primitives --------
def draw_mark(c: canvas.Canvas, cx, cy, size, color=ACCENT, stroke=None):
    """Render the Free to Build mark (triangle + door) centered at (cx, cy)."""
    if stroke is None:
        stroke = max(2.0, size * 0.09)
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(stroke)
    c.setLineJoin(1)  # round
    c.setLineCap(1)
    s = size / 40.0
    x0 = cx - (size / 2)
    y0 = cy - (size / 2)

    def pt(px, py):
        # SVG y goes down; PDF y goes up. Input uses SVG coords (0..40).
        return x0 + px * s, y0 + (40 - py) * s

    # Triangle M4 34 L20 6 L36 34 Z
    p = c.beginPath()
    p.moveTo(*pt(4, 34))
    p.lineTo(*pt(20, 6))
    p.lineTo(*pt(36, 34))
    p.close()
    c.drawPath(p, stroke=1, fill=0)
    # Door M14 34 V22 H26 V34
    p2 = c.beginPath()
    p2.moveTo(*pt(14, 34))
    p2.lineTo(*pt(14, 22))
    p2.lineTo(*pt(26, 22))
    p2.lineTo(*pt(26, 34))
    c.drawPath(p2, stroke=1, fill=0)
    c.restoreState()


def bg_dark(c: canvas.Canvas):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # subtle grid
    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    step = 14 * mm
    y = 0
    while y < H:
        c.line(0, y, W, y)
        y += step
    x = 0
    while x < W:
        c.line(x, 0, x, H)
        x += step
    # glow blobs (faked with stacked circles w/ alpha)
    for i, (r, col, cx, cy) in enumerate([
        (120 * mm, Color(1, 87/255, 34/255, alpha=0.06), 30 * mm, H - 30 * mm),
        (100 * mm, Color(1, 183/255, 3/255, alpha=0.05), W - 30 * mm, 40 * mm),
    ]):
        c.setFillColor(col)
        c.circle(cx, cy, r, stroke=0, fill=1)


def bg_light(c: canvas.Canvas):
    c.setFillColor(FG)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def hash_badge(c: canvas.Canvas, cx, y, size=9):
    c.setFont("Helvetica-Bold", size)
    text = "#FREETOBUILD"
    tw = c.stringWidth(text, "Helvetica-Bold", size)
    c.setFillColor(ACCENT)
    c.drawString(cx - tw / 2, y, text)


# -------- text helpers --------
def draw_title(c, text, y, color=FG, size=46, font="Helvetica-Bold", x=MARGIN, max_w=None):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)
    return y - size * 1.05


def wrap_lines(text, font, size, max_w, c):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if c.stringWidth(trial, font, size) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(c, text, x, y, max_w, size=11, color=INK, font="Helvetica", leading=None):
    if leading is None:
        leading = size * 1.5
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_lines(text, font, size, max_w, c):
        c.drawString(x, y, line)
        y -= leading
    return y


def page_footer(c, page_num, total, mode="dark"):
    c.setFont("Helvetica", 8)
    if mode == "dark":
        c.setFillColor(FG_DIM)
    else:
        c.setFillColor(HexColor("#666666"))
    c.drawString(MARGIN, 14 * mm, "FREE TO BUILD  ·  freetobuild.github.io  ·  CC0")
    c.drawRightString(W - MARGIN, 14 * mm, f"{page_num} / {total}")


# =========================================================
# MANIFESTO
# =========================================================
def build_manifesto():
    path = ASSETS / "freetobuild-manifesto.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("The Free to Build Manifesto")
    c.setAuthor("Free to Build")
    c.setSubject("Build where you stand. No permission required.")
    c.setKeywords(["free to build", "manifesto", "land", "housing", "off-grid"])

    # ---------- Page 1: cover ----------
    bg_dark(c)
    draw_mark(c, W / 2, H - 60 * mm, 34 * mm, ACCENT, stroke=3.4)

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(FG_DIM)
    c.drawCentredString(W / 2, H - 92 * mm, "A MANIFESTO · 2026 · CC0")

    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, H / 2 + 6 * mm, "BUILD")
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, H / 2 - 22 * mm, "WHERE YOU")
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, H / 2 - 50 * mm, "STAND.")

    c.setFont("Helvetica", 11)
    c.setFillColor(FG_DIM)
    c.drawCentredString(W / 2, 40 * mm, "No permits. No licenses. No fees. No one's permission required.")
    c.drawCentredString(W / 2, 34 * mm, "Housing is a birthright — not a privilege.")

    hash_badge(c, W / 2, 20 * mm, size=10)
    c.showPage()

    # ---------- helper for light content pages ----------
    def content_page(title_big, title_accent, paragraphs, page_num, total):
        bg_light(c)
        # small mark top-left
        draw_mark(c, MARGIN + 7 * mm, H - 22 * mm, 14 * mm, ACCENT, stroke=1.6)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor("#777777"))
        c.drawString(MARGIN + 20 * mm, H - 20 * mm, "FREE TO BUILD  ·  MANIFESTO")

        y = H - 48 * mm
        c.setFont("Helvetica-Bold", 34)
        c.setFillColor(INK)
        c.drawString(MARGIN, y, title_big)
        y -= 13 * mm
        c.setFont("Helvetica-Bold", 34)
        c.setFillColor(ACCENT)
        c.drawString(MARGIN, y, title_accent)
        y -= 16 * mm

        max_w = W - 2 * MARGIN
        for p in paragraphs:
            if p.startswith("§"):  # subhead
                y -= 4 * mm
                c.setFont("Helvetica-Bold", 13)
                c.setFillColor(INK)
                c.drawString(MARGIN, y, p[1:].strip().upper())
                y -= 7 * mm
                continue
            y = draw_paragraph(c, p, MARGIN, y, max_w, size=11.5, color=INK, leading=17)
            y -= 4 * mm
            if y < 30 * mm:
                break

        page_footer(c, page_num, total, mode="light")
        c.showPage()

    TOTAL = 6

    # ---------- Page 2: The Problem ----------
    content_page(
        "THE",
        "PROBLEM.",
        [
            "Every other animal on Earth builds its own shelter. Birds, beavers, bees — none of them ask for permission, pay a license, file a plan, or hire an inspector. They just build.",
            "We used to do the same. For most of human history, a human could walk into an unclaimed forest or field and raise a roof. It was not a utopia; it was simply the default.",
            "Then, slowly, we criminalized it. Permits, licenses, zoning codes, fees, inspections, and the quiet claim that every square meter of the planet already belongs to someone — usually someone who never set foot on it.",
            "The result: a manufactured housing crisis on every continent. Millions of adults trapped, priced out, or homeless, while empty land stretches in every direction. We built a world where the simple act of sheltering yourself is illegal.",
            "This is not freedom. This is not civilization. This is a cage we agreed to — and can disagree with.",
        ],
        2, TOTAL,
    )

    # ---------- Page 3: The Principles ----------
    content_page(
        "THE",
        "PRINCIPLES.",
        [
            "§ 01 Freedom to Build",
            "No permits. No licenses. No fees. If you can build it and maintain it, you may build it.",
            "§ 02 Claim Unclaimed Land",
            "If land is truly unowned, unused, and neglected, it belongs to whoever stands on it, improves it, and does not leave.",
            "§ 03 No Housing Regulations",
            "Your shelter, your rules. Safety is your responsibility. Adult human beings are capable of judging whether their own roof will hold.",
            "§ 04 Hope for All",
            "For the broke, the young, the displaced, the adventurous, the families who just want a roof they own. No movement has the right to lock out the next generation.",
            "§ 05 Peaceful Revolution",
            "We build. We document. We share. We grow. No violence — just unstoppable creation, and the slow, loud reassertion of a right older than any state.",
        ],
        3, TOTAL,
    )

    # ---------- Page 4: The 4+1 Standard ----------
    content_page(
        "THE 4+1",
        "STANDARD.",
        [
            "The movement takes a position on how long the original owner of neglected land should retain the right to object before a new occupant's claim becomes permanent.",
            "The Free to Build standard is simple: no more than five years.",
            "§ Up to year 4",
            "The original owner may, at any time, come forward, prove their title, and reclaim the land. The new occupant must leave, with compensation for documented improvements where the law provides for it.",
            "§ Years 4 to 5",
            "Any peaceful, visible, improving occupant may file a formal claim. The window is public. It can be challenged. It must be undefeated for one further year.",
            "§ After year 5",
            "If the original owner has not acted in five years, the land belongs — in law and in conscience — to the person who has lived on it, built on it, and cared for it.",
            "Five years is, by global historical standards, already lenient. Many jurisdictions already meet or beat it; many more should.",
        ],
        4, TOTAL,
    )

    # ---------- Page 5: What You Can Do Today ----------
    content_page(
        "DO IT",
        "TODAY.",
        [
            "§ 01 Spread the word",
            "Post with #FreeToBuild. Share your story. Tell your family. Tell the stranger next to you on the bus. A movement is just a sentence repeated by many mouths.",
            "§ 02 Start building",
            "Find unclaimed land in a friendly jurisdiction. Put a stake in the ground. Raise a small shelter. Plant a garden. Document everything in public — dated, timestamped, unashamed.",
            "§ 03 Contribute",
            "Stories, photos, legal research, DIY guides, maps, art, manifestos. The open repository at github.com/FreeToBuild is the hub. There is no gatekeeper. Pull requests welcome.",
            "§ 04 Fund the fight",
            "Direct giving, fiscal hosts, grants, stipends — see freetobuild.github.io/fund. Every euro funds research, builders on the ground, and the legal work to defend them.",
            "§ 05 Don't wait for permission",
            "That was always the point.",
        ],
        5, TOTAL,
    )

    # ---------- Page 6: Closing ----------
    bg_dark(c)
    draw_mark(c, W / 2, H - 70 * mm, 30 * mm, ACCENT, stroke=3.0)

    c.setFont("Helvetica-Bold", 54)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, H / 2 + 20 * mm, "THE FUTURE")
    c.setFont("Helvetica-Bold", 54)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, H / 2 - 4 * mm, "DOESN'T NEED")
    c.setFont("Helvetica-Bold", 70)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, H / 2 - 40 * mm, "PERMISSION.")

    c.setFont("Helvetica", 10)
    c.setFillColor(FG_DIM)
    c.drawCentredString(W / 2, 46 * mm, "Free to Build · est. 2026 · released under CC0 1.0")
    c.drawCentredString(W / 2, 40 * mm, "freetobuild.github.io  ·  github.com/FreeToBuild")
    hash_badge(c, W / 2, 28 * mm, size=12)

    page_footer(c, 6, TOTAL, mode="dark")
    c.showPage()

    c.save()
    size_kb = path.stat().st_size // 1024
    print(f"  wrote {path.name} ({size_kb} KB, {TOTAL} pages)")


# =========================================================
# EVIDENCE DECK / PRESS KIT
# =========================================================
def build_press_kit():
    path = ASSETS / "freetobuild-press-kit.pdf"
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setTitle("Free to Build — Evidence Deck")
    c.setAuthor("Free to Build")
    c.setSubject("A one-document briefing for press, policy, and funders.")
    c.setKeywords(["free to build", "press kit", "evidence", "adverse possession", "allodial"])

    def header(c, title):
        c.setFillColor(FG)
        bg_light(c)
        draw_mark(c, MARGIN + 7 * mm, H - 22 * mm, 14 * mm, ACCENT, stroke=1.6)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(HexColor("#777777"))
        c.drawString(MARGIN + 20 * mm, H - 20 * mm, "FREE TO BUILD  ·  EVIDENCE DECK")
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(W - MARGIN, H - 20 * mm, title.upper())

    TOTAL = 6

    # ---------- Cover ----------
    bg_dark(c)
    draw_mark(c, W / 2, H - 60 * mm, 32 * mm, ACCENT, stroke=3.2)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, H - 92 * mm, "EVIDENCE DECK  ·  2026  ·  CC0")

    c.setFont("Helvetica-Bold", 72)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, H / 2 + 20 * mm, "FREE TO")
    c.setFont("Helvetica-Bold", 72)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, H / 2 - 6 * mm, "BUILD.")

    c.setFont("Helvetica", 12)
    c.setFillColor(FG_DIM)
    c.drawCentredString(W / 2, H / 2 - 36 * mm, "A one-document briefing for press, policy, and funders.")

    c.setFont("Helvetica", 10)
    c.drawCentredString(W / 2, 40 * mm, "freetobuild.github.io  ·  github.com/FreeToBuild")
    c.drawCentredString(W / 2, 34 * mm, "Released under CC0 1.0 — no rights reserved.")
    hash_badge(c, W / 2, 20 * mm, size=10)
    c.showPage()

    # ---------- Page 2: Thesis + Stats ----------
    header(c, "Thesis")
    y = H - 48 * mm
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(INK)
    c.drawString(MARGIN, y, "Cities were a compromise")
    y -= 11 * mm
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "with scarcity.")
    y -= 16 * mm

    paragraphs = [
        "For the first time in human history, a single person with a few thousand euros can build a home, power it, feed a family, stay connected, and live far from any city — comfortably, legally, and indefinitely.",
        "The only remaining obstacle between a human being and a self-built, self-owned, off-grid home is the legal fiction that they need someone's permission. That is the single lever this movement pulls.",
    ]
    max_w = W - 2 * MARGIN
    for p in paragraphs:
        y = draw_paragraph(c, p, MARGIN, y, max_w, size=11.5, color=INK, leading=17)
        y -= 4 * mm

    # Stat row
    y -= 4 * mm
    stats = [
        ("~90%", "fall in solar PV price per watt, 2014–2024"),
        ("~50%", "fall in LFP battery cost, 2021–2024"),
        ("< €50/mo", "LEO satellite internet, anywhere on the continent"),
        ("< €15k", "material cost for a warm, 40 m² timber cabin"),
    ]
    box_w = (max_w - 3 * 6 * mm) / 4
    box_h = 30 * mm
    bx = MARGIN
    for big, small in stats:
        c.setFillColor(HexColor("#f1ede3"))
        c.roundRect(bx, y - box_h, box_w, box_h, 8, stroke=0, fill=1)
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(bx + 6 * mm, y - 13 * mm, big)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.5)
        for i, line in enumerate(wrap_lines(small, "Helvetica", 8.5, box_w - 10 * mm, c)):
            c.drawString(bx + 6 * mm, y - 18 * mm - i * 10, line)
        bx += box_w + 6 * mm

    page_footer(c, 2, TOTAL, mode="light")
    c.showPage()

    # ---------- Page 3: The 4+1 standard ----------
    header(c, "The 4+1 Standard")
    y = H - 48 * mm
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(INK)
    c.drawString(MARGIN, y, "Four years to object.")
    y -= 11 * mm
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "One year to confirm.")
    y -= 16 * mm

    for p in [
        "The movement's position on how long a neglectful owner retains the right to reclaim abandoned land is, by global historical standards, lenient.",
        "§ Up to year 4 — the original owner may at any time prove title and reclaim the land, with compensation for documented improvements as the law provides.",
        "§ Years 4 to 5 — any peaceful, visible, improving occupant may file a public claim. It can be challenged. It must remain undefeated for one year.",
        "§ After year 5 — if the owner has not acted, the land belongs to the person who lives on it, builds it, and does not leave.",
    ]:
        if p.startswith("§"):
            y -= 3 * mm
            c.setFillColor(ACCENT)
            c.setFont("Helvetica-Bold", 12)
            parts = p[1:].strip().split(" — ", 1)
            c.drawString(MARGIN, y, parts[0].upper())
            y -= 6 * mm
            if len(parts) > 1:
                y = draw_paragraph(c, parts[1], MARGIN, y, max_w, size=11.5, color=INK, leading=16)
                y -= 3 * mm
        else:
            y = draw_paragraph(c, p, MARGIN, y, max_w, size=11.5, color=INK, leading=17)
            y -= 4 * mm
    page_footer(c, 3, TOTAL, mode="light")
    c.showPage()

    # ---------- Page 4: Adverse possession table ----------
    header(c, "Adverse Possession Atlas")
    y = H - 48 * mm
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(INK)
    c.drawString(MARGIN, y, "Where you can claim land today.")
    y -= 10 * mm
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#444444"))
    c.drawString(MARGIN, y, "Minimum adverse-possession / positive-prescription period, typical good-faith conditions.")
    y -= 10 * mm

    # Table
    rows = [
        ("USA — Montana", "5 yrs", "Shortest standard period in the Western world. Property-tax condition."),
        ("Scotland", "10 yrs", "Positive prescription. Fastest in Europe."),
        ("Finland", "10 yrs", "Good faith + registered title under the Land Code."),
        ("France", "10 yrs", "Usucapion abrégée with juste titre and good faith."),
        ("Spain", "10 yrs", "Immovable property, good-faith + title. 30 yrs otherwise."),
        ("England & Wales", "10–12", "Registered vs unregistered land, LRA 2002."),
        ("Ireland", "12 yrs", "Statute of Limitations; works on both registered and unregistered land."),
        ("Moldova · Georgia · Ukraine", "15 yrs", "Post-Soviet civil codes; abundant rural land."),
        ("Albania · Serbia", "10–20", "10 yrs good faith, 20 yrs extraordinary."),
        ("Norway · Sweden", "20 yrs", "Hevd / hävd. Strong cultural legitimacy."),
        ("Italy · Iceland", "20 yrs", "Usucapione / hefð."),
        ("Germany", "30 yrs", "Ersitzung. Strongly disfavored for land in practice."),
    ]
    col_x = [MARGIN, MARGIN + 72 * mm, MARGIN + 100 * mm]
    col_w = [70 * mm, 26 * mm, max_w - 98 * mm]

    # header row
    c.setFillColor(HexColor("#f1ede3"))
    c.rect(MARGIN, y - 9 * mm, max_w, 9 * mm, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(col_x[0] + 3 * mm, y - 6 * mm, "JURISDICTION")
    c.drawString(col_x[1] + 3 * mm, y - 6 * mm, "MIN. YEARS")
    c.drawString(col_x[2] + 3 * mm, y - 6 * mm, "NOTES")
    y -= 11 * mm

    for jur, yrs, note in rows:
        row_h = 10 * mm
        c.setStrokeColor(HexColor("#e0dccf"))
        c.setLineWidth(0.4)
        c.line(MARGIN, y + 4 * mm, MARGIN + max_w, y + 4 * mm)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(INK)
        c.drawString(col_x[0] + 3 * mm, y, jur)
        c.setFont("Helvetica-Bold", 9.5)
        c.setFillColor(ACCENT)
        c.drawString(col_x[1] + 3 * mm, y, yrs)
        c.setFont("Helvetica", 8.8)
        c.setFillColor(HexColor("#333333"))
        lines = wrap_lines(note, "Helvetica", 8.8, col_w[2] - 3 * mm, c)
        for i, line in enumerate(lines[:2]):
            c.drawString(col_x[2] + 3 * mm, y - i * 10, line)
        y -= row_h

    page_footer(c, 4, TOTAL, mode="light")
    c.showPage()

    # ---------- Page 5: Allodial rights ----------
    header(c, "Allodial Rights")
    y = H - 48 * mm
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(INK)
    c.drawString(MARGIN, y, "Allodial title:")
    y -= 11 * mm
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN, y, "Land owned outright.")
    y -= 14 * mm

    for p in [
        "Most property in the world today is held under some form of feudal derivation — even 'freehold' is technically held of the Crown or the state. Allodial title is the older and purer form: land owned absolutely, with no superior lord.",
        "§ Orkney & Shetland (Scotland) — Udal Law, inherited from Norway. The purest surviving allodial system in Europe.",
        "§ Norway — Odelsrett, the ancient right of kin to reclaim ancestral farmland.",
        "§ Faroe Islands — Retains óðal traditions close to Orkney's.",
        "§ Andorra — Strong tradition of absolute private ownership.",
        "§ Scotland — The Abolition of Feudal Tenure etc. Act 2000 abolished feudal superiority; freehold is now near-allodial.",
        "§ USA — Nevada and Texas — Limited statutory provisions for purchasing allodial status.",
    ]:
        if p.startswith("§"):
            y -= 2 * mm
            parts = p[1:].strip().split(" — ", 1)
            c.setFillColor(ACCENT)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(MARGIN, y, parts[0])
            y -= 5.5 * mm
            if len(parts) > 1:
                y = draw_paragraph(c, parts[1], MARGIN, y, max_w, size=10.5, color=INK, leading=15)
                y -= 2 * mm
        else:
            y = draw_paragraph(c, p, MARGIN, y, max_w, size=11, color=INK, leading=16)
            y -= 4 * mm
    page_footer(c, 5, TOTAL, mode="light")
    c.showPage()

    # ---------- Page 6: How to support ----------
    bg_dark(c)
    draw_mark(c, W / 2, H - 55 * mm, 26 * mm, ACCENT, stroke=2.6)

    y = H - 90 * mm
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(FG)
    c.drawCentredString(W / 2, y, "HOW TO SUPPORT")
    y -= 10 * mm
    c.setFont("Helvetica-Bold", 40)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, y, "THIS MOVEMENT.")
    y -= 18 * mm

    lines = [
        ("COVER IT", "Press inquiries: press@freetobuild.org. We reply fast."),
        ("FUND IT", "GitHub Sponsors, Liberapay, Ko-fi, Open Collective Europe, SEPA, crypto."),
        ("GRANT IT", "NLnet, Sovereign Tech Fund, Shuttleworth, Open Society, Emergent Ventures, Prototype Fund, Mozilla."),
        ("BUILD IT", "Find unclaimed land. Put down stakes. Document everything in public."),
        ("SHARE IT", "Post with #FreeToBuild. Print this page. Put it on a wall."),
    ]
    for tag, body in lines:
        c.setFillColor(ACCENT)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGIN + 6 * mm, y, tag)
        c.setFillColor(FG)
        c.setFont("Helvetica", 11)
        for i, line in enumerate(wrap_lines(body, "Helvetica", 11, W - 2 * MARGIN - 38 * mm, c)):
            c.drawString(MARGIN + 34 * mm, y - i * 13, line)
        y -= 16 * mm

    c.setFont("Helvetica", 10)
    c.setFillColor(FG_DIM)
    c.drawCentredString(W / 2, 30 * mm, "freetobuild.github.io  ·  github.com/FreeToBuild  ·  CC0 1.0")
    hash_badge(c, W / 2, 20 * mm, size=11)

    page_footer(c, 6, TOTAL, mode="dark")
    c.showPage()

    c.save()
    size_kb = path.stat().st_size // 1024
    print(f"  wrote {path.name} ({size_kb} KB, {TOTAL} pages)")


if __name__ == "__main__":
    print("Generating PDFs...")
    build_manifesto()
    build_press_kit()
    print(f"\nDone. Files in: {ASSETS}")
