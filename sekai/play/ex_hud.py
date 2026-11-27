from sonolus.script.bucket import Judgment
from sonolus.script.quad import Rect
from sonolus.script.runtime import time
from sekai.lib.layout import Layout
from sekai.lib.layer import get_z_alt, layers
from sekai.lib.options import Options
from sekai.lib.skin import BaseSkin
from sekai.play.common import PlayLevelMemory as M


def record_judgment(judgment: Judgment, error: float):
    if judgment == Judgment.PERFECT:
        M.ex_perfect += 1
    elif judgment == Judgment.GREAT:
        M.ex_great += 1
    elif judgment == Judgment.GOOD:
        M.ex_good += 1
    elif judgment == Judgment.MISS:
        M.ex_miss += 1
    if judgment == Judgment.MISS or judgment == Judgment.GOOD:
        M.ex_combo = 0
    else:
        M.ex_combo += 1
    if judgment != Judgment.MISS:
        M.ex_error_ms = error * 1000
        M.ex_last_hit = time()
    else:
        M.ex_last_hit = -100


def rank_for_counts(perfect: int, great: int, good: int, miss: int) -> int:
    total = perfect + great + good + miss
    if total == 0 or perfect == total:
        return 8
    accuracy = (perfect + 0.7 * great + 0.5 * good) / total
    if accuracy >= 0.99:
        return 7
    if accuracy >= 0.97:
        return 6
    if accuracy >= 0.93:
        return 5
    if accuracy >= 0.85:
        return 4
    if accuracy >= 0.75:
        return 3
    if accuracy >= 0.60:
        return 2
    return 1


def update_rank():
    rank = rank_for_counts(M.ex_perfect, M.ex_great, M.ex_good, M.ex_miss)
    if rank != M.ex_rank:
        M.ex_rank = rank
        M.ex_rank_changed = time()


def draw_rank():
    if Options.hide_ui:
        return
    index = M.ex_rank
    if index == 8:
        index = 8 + int(time() * 6) % 12
    scale = 1 + 0.18 * max(0.0, 1 - (time() - M.ex_rank_changed) / 0.2)
    x = -Layout.field_w * 0.355
    y = Layout.field_h * 0.11
    w = Layout.field_h * 0.30 * scale
    h = w * 0.5
    if Options.ex_rank_enabled:
        BaseSkin.ex_rank[index].draw(Rect(l=x-w/2, r=x+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 2000).tuple, a=1)

    draw_details(x, y)


def glyph(index: int, x: float, y: float, w: float, h: float):
    BaseSkin.ex_labels[index].draw(Rect(l=x-w/2, r=x+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 2001).tuple, a=1)


def digits(value: int, count: int, x: float, y: float, h: float):
    w = h * 0.62
    for i in range(count):
        digit = value % 10
        dx = x + (count / 2 - i - 0.5) * w
        BaseSkin.ex_digits[digit].draw(Rect(l=dx-w/2, r=dx+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 2002).tuple, a=1)
        value = value // 10


def draw_details(x: float, y: float):
    h = Layout.field_h
    total = M.ex_perfect + M.ex_great + M.ex_good + M.ex_miss
    if Options.ex_accuracy_enabled:
        accuracy = 10000
        if total > 0:
            accuracy = int((M.ex_perfect + 0.7*M.ex_great + 0.5*M.ex_good)*10000/total + 0.5)
        yy = y - h*0.105
        digits(accuracy//100, 3, x-h*0.043, yy, h*0.035)
        glyph(4, x, yy, h*0.012, h*0.035)
        digits(accuracy%100, 2, x+h*0.028, yy, h*0.035)
        glyph(5, x+h*0.065, yy, h*0.025, h*0.035)
    if Options.ex_counts_enabled:
        for i in range(4):
            yy = y-h*(0.16+i*0.043)
            glyph(i, x-h*0.047, yy, h*0.12, h*0.034)
            value = M.ex_perfect
            if i == 1:
                value = M.ex_great
            elif i == 2:
                value = M.ex_good
            elif i == 3:
                value = M.ex_miss
            digits(value, 4, x+h*0.065, yy, h*0.032)
    if Options.ex_status_enabled and total > 0:
        if M.ex_perfect == total:
            glyph(8, -x, y-h*0.105, h*0.22, h*0.04)
        elif M.ex_miss == 0 and M.ex_good == 0:
            glyph(9, -x, y-h*0.105, h*0.22, h*0.04)
    if Options.ex_timing_enabled and time()-M.ex_last_hit < 0.65:
        yy = -h*0.17
        if M.ex_error_ms < 0:
            glyph(6, -h*0.085, yy, h*0.09, h*0.035)
        elif M.ex_error_ms > 0:
            glyph(7, -h*0.085, yy, h*0.09, h*0.035)
        digits(int(abs(M.ex_error_ms)+0.5), 3, h*0.015, yy, h*0.035)
        glyph(10, h*0.07, yy, h*0.04, h*0.035)
