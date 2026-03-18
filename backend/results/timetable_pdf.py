from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Monochrome palette ──────────────────────────────────────────────────────
BLACK        = colors.black
WHITE        = colors.white
DARK_GREY    = colors.HexColor("#1a1a1a")   # near-black for headers
MID_GREY     = colors.HexColor("#555555")   # lines, secondary text
LIGHT_GREY   = colors.HexColor("#cccccc")   # grid lines
VERY_LIGHT   = colors.HexColor("#f2f2f2")   # alternating row shade
BREAK_SHADE  = colors.HexColor("#e8e8e8")   # break/lunch column fill


def _build_column_slots(config):
    """Build ordered list of column descriptors (period|break|lunch).

    Lunch/break are inserted AFTER the period whose index equals
    lunch_after_period / short_break_after_period (0-based).
    """
    start_time          = config["start_time"]
    period_minutes      = config["period_minutes"]
    periods_per_day     = config["periods_per_day"]
    lunch_after         = config["lunch_after_period"]
    lunch_minutes       = config.get("lunch_minutes", 40)
    short_break_after   = config.get("short_break_after_period")
    short_break_minutes = config.get("short_break_minutes", 10) or 10

    h, m = map(int, start_time.split(":"))
    cur  = h * 60 + m

    def fmt(t):
        return "{:02d}:{:02d}".format((t // 60) % 24, t % 60)

    cols = []
    tidx = 0
    for p in range(periods_per_day):
        s, e = cur, cur + period_minutes
        cols.append({
            "kind":       "period",
            "period_idx": tidx,
            "title":      "{}\n{}".format(fmt(s), fmt(e)),
        })
        cur  += period_minutes
        tidx += 1

        if short_break_after is not None and p == short_break_after:
            bs, be = cur, cur + short_break_minutes
            cols.append({
                "kind":  "break",
                "title": "SHORT\nBREAK\n{}-{}".format(fmt(bs), fmt(be)),
            })
            cur += short_break_minutes

        if lunch_after is not None and p == lunch_after:
            ls, le = cur, cur + lunch_minutes
            cols.append({
                "kind":  "lunch",
                "title": "LUNCH\nBREAK\n{}-{}".format(fmt(ls), fmt(le)),
            })
            cur += lunch_minutes

    return cols


def _ps(name, **kw):
    base = getSampleStyleSheet()["Normal"]
    return ParagraphStyle(name, parent=base, **kw)


DAYS_SHORT = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]


def _section_story(config, solution, section, metadata, col_slots=None):
    """Return list of Flowables for one section timetable page."""
    story           = []
    working_days    = config["working_days"]
    periods_per_day = config["periods_per_day"]

    if col_slots is None:
        col_slots = _build_column_slots(config)

    # ── Paragraph styles ────────────────────────────────────────────────────
    title_st     = _ps("ts",   fontSize=14, fontName="Helvetica-Bold",
                        textColor=BLACK,     alignment=TA_CENTER, spaceAfter=2)
    sub_st       = _ps("ss",   fontSize=9,  fontName="Helvetica",
                        textColor=DARK_GREY, alignment=TA_CENTER, spaceAfter=4)
    hdr_day      = _ps("hd",   fontSize=8,  fontName="Helvetica-Bold",
                        textColor=WHITE,     alignment=TA_CENTER, leading=10)
    hdr_time     = _ps("ht",   fontSize=6,  fontName="Helvetica-Bold",
                        textColor=BLACK,     alignment=TA_CENTER, leading=7)
    cell_norm    = _ps("cn",   fontSize=7,  alignment=TA_CENTER, leading=9,
                        textColor=BLACK)
    cell_it      = _ps("ci",   fontSize=7,  fontName="Helvetica-Oblique",
                        alignment=TA_CENTER, leading=9, textColor=MID_GREY)
    cell_bold    = _ps("cb",   fontSize=7,  fontName="Helvetica-Bold",
                        alignment=TA_CENTER, leading=9, textColor=BLACK)
    cell_brk     = _ps("cbr",  fontSize=6,  fontName="Helvetica-Bold",
                        alignment=TA_CENTER, leading=8, textColor=BLACK)
    leg_hdr_st   = _ps("lhdr", fontSize=10, fontName="Helvetica-Bold",
                        textColor=BLACK,     alignment=TA_LEFT,
                        spaceBefore=4, spaceAfter=4)
    sig_bold     = _ps("sgb",  fontSize=9,  fontName="Helvetica-Bold",
                        textColor=BLACK,     alignment=TA_CENTER)
    footer_st    = _ps("ft",   fontSize=7,  textColor=MID_GREY,
                        alignment=TA_CENTER, spaceBefore=6)
    leg_cell     = _ps("lc",   fontSize=8,  textColor=BLACK, alignment=TA_LEFT)
    leg_cell_c   = _ps("lcc",  fontSize=8,  textColor=BLACK, alignment=TA_CENTER)
    leg_hdr_cell = _ps("lhc",  fontSize=8,  fontName="Helvetica-Bold",
                        textColor=WHITE,     alignment=TA_CENTER)

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph(metadata["college_name"], title_st))
    yr  = metadata.get("year", "")
    br  = metadata.get("branch", "")
    sem = metadata.get("semester", "")
    rm  = metadata.get("room", "__________")
    story.append(Paragraph(
        "Class: {} {} {} Sem \u2013 {} Section"
        "&nbsp;&nbsp;&nbsp;&nbsp;Room Number: {}".format(yr, br, sem, section, rm),
        sub_st,
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLACK, spaceAfter=6))

    # ── Grid ────────────────────────────────────────────────────────────────
    header_row = [Paragraph("DAY / TIME", hdr_day)]
    for cs in col_slots:
        if cs["kind"] == "period":
            header_row.append(Paragraph(cs["title"], hdr_time))
        else:
            header_row.append(Paragraph(cs["title"], cell_brk))

    table_data = [header_row]
    for d in range(working_days):
        row = [Paragraph(DAYS_SHORT[d], hdr_day)]
        for cs in col_slots:
            if cs["kind"] in ("break", "lunch"):
                row.append(Paragraph("", cell_norm))
                continue
            p  = cs["period_idx"]
            si = solution.get((d, p))
            if si is None:
                row.append(Paragraph("", cell_norm))
            elif si.get("is_lab_cont"):
                row.append(Paragraph("(cont.)", cell_it))
            else:
                stype = si.get("type", "theory")
                sname = si.get("subject_name", "")
                txt   = "LAB\n({})".format(sname) if stype == "lab" else sname
                row.append(Paragraph(txt, cell_bold))
        table_data.append(row)

    # ── Column widths ───────────────────────────────────────────────────────
    page_w      = landscape(A4)[0] - 3 * cm
    day_col_w   = 1.3 * cm
    break_col_w = 1.4 * cm
    lunch_col_w = 1.8 * cm
    n_break  = sum(1 for cs in col_slots if cs["kind"] == "break")
    n_lunch  = sum(1 for cs in col_slots if cs["kind"] == "lunch")
    n_period = sum(1 for cs in col_slots if cs["kind"] == "period")
    remain   = page_w - day_col_w - n_break * break_col_w - n_lunch * lunch_col_w
    per_w    = remain / max(n_period, 1)

    col_widths = [day_col_w]
    for cs in col_slots:
        if cs["kind"] == "period":
            col_widths.append(per_w)
        elif cs["kind"] == "break":
            col_widths.append(break_col_w)
        else:
            col_widths.append(lunch_col_w)

    tbl  = Table(table_data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  DARK_GREY),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
        ("BACKGROUND",    (0, 1), (0, -1),  DARK_GREY),
        ("TEXTCOLOR",     (0, 1), (0, -1),  WHITE),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.5, LIGHT_GREY),
        ("LIN
