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
    M.ex_error_ms = error * 1000


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
    if Options.hide_ui or not Options.ex_rank_enabled:
        return
    index = M.ex_rank
    if index == 8:
        index = 8 + int(time() * 6) % 12
    scale = 1 + 0.18 * max(0.0, 1 - (time() - M.ex_rank_changed) / 0.2)
    x = -Layout.field_w * 0.355
    y = Layout.field_h * 0.11
    w = Layout.field_h * 0.24 * scale
    h = w * 0.5
    BaseSkin.ex_rank[index].draw(Rect(l=x-w/2, r=x+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 2000).tuple, a=1)
