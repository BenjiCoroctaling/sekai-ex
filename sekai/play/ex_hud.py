from sonolus.script.bucket import Judgment
from sonolus.script.quad import Rect
from sonolus.script.runtime import is_watch, is_replay, safe_area, screen, time
from sekai.lib.layout import Layout
from sekai.lib.note import NoteKind
from sekai.lib.layer import get_z_alt, layers
from sekai.lib.options import Options
from sekai.lib.skin import BaseSkin
from sekai.play.common import PlayLevelMemory as M


def register_note(target: float):
    M.ex_note_total += 1
    M.ex_end_time = max(M.ex_end_time, target)


def miss_cost(kind: NoteKind) -> int:
    if kind == NoteKind.NORM_TICK or kind == NoteKind.CRIT_TICK or kind == NoteKind.HIDE_TICK or kind == NoteKind.DAMAGE or kind == NoteKind.HIDE_DAMAGE_TICK:
        return 40
    return 80


def record_judgment(judgment: Judgment, error: float, kind: NoteKind):
    if judgment == Judgment.PERFECT:
        M.ex_perfect += 1
    elif judgment == Judgment.GREAT:
        M.ex_great += 1
    elif judgment == Judgment.GOOD:
        M.ex_good += 1
    elif judgment == Judgment.MISS:
        M.ex_miss += 1
        M.ex_life = max(0, M.ex_life - miss_cost(kind))
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
    update_visuals()
    rank = rank_for_counts(M.ex_perfect, M.ex_great, M.ex_good, M.ex_miss)
    if M.ex_life <= 0:
        rank = 0
    if M.ex_combo > 0 and M.ex_combo // 100 > M.ex_milestone // 100:
        M.ex_milestone = M.ex_combo // 100 * 100
        M.ex_milestone_time = time()
    if M.ex_combo < M.ex_milestone:
        M.ex_milestone = M.ex_combo // 100 * 100
        M.ex_milestone_time = -100
    if rank != M.ex_rank:
        M.ex_rank = rank
        M.ex_rank_changed = time()


def update_visuals():
    now = time()
    dt = now - M.ex_visual_time
    target = min(1.0, M.ex_combo / 1000.0)
    ap = 0.0
    fc = 0.0
    if M.ex_great + M.ex_good + M.ex_miss == 0:
        ap = 1.0
    elif M.ex_good + M.ex_miss == 0:
        fc = 1.0
    if dt < 0 or dt > 0.5:
        M.ex_aura_level = target
        M.ex_aura_ap = ap
        M.ex_aura_fc = fc
        M.ex_display_life = M.ex_life
    else:
        k = min(1.0, dt * 5)
        M.ex_aura_level += (target - M.ex_aura_level) * k
        M.ex_aura_ap += (ap - M.ex_aura_ap) * k
        M.ex_aura_fc += (fc - M.ex_aura_fc) * k
        M.ex_display_life += (M.ex_life - M.ex_display_life) * min(1.0, dt * 9)
    M.ex_visual_time = now


def draw_rank():
    if Options.hide_ui:
        return
    index = M.ex_rank
    if index == 8:
        index = 8 + int(time() * 6) % 12
    age = max(0.0, time() - M.ex_rank_changed)
    impact = max(0.0, 1 - age / 0.42)
    scale = 1 + (0.10 + M.ex_rank * 0.025) * impact * impact
    x = max(safe_area().l + Layout.field_h * 0.17, -Layout.field_w * 0.455)
    y = Layout.field_h * 0.11
    w = Layout.field_h * 0.30 * scale
    h = w * 0.5
    if Options.ex_rank_enabled:
        if impact > 0 and M.ex_rank != 8:
            spread = 1.0 + 0.65 * (1-impact)
            BaseSkin.ex_rank[index].draw(Rect(l=x-w*spread/2,r=x+w*spread/2,b=y-h*spread/2,t=y+h*spread/2).as_quad(),z=get_z_alt(layers.overlay,8999).tuple,a=0.32*impact)
        if M.ex_rank == 6 or M.ex_rank == 7:
            pulse = abs((time() % 1.6) / 0.8 - 1)
            glow = 1.10 + 0.07 * pulse
            BaseSkin.ex_rank[index].draw(Rect(l=x-w*glow/2, r=x+w*glow/2, b=y-h*glow/2, t=y+h*glow/2).as_quad(), z=get_z_alt(layers.overlay, 8999).tuple, a=0.16+0.12*pulse)
        BaseSkin.ex_rank[index].draw(Rect(l=x-w/2, r=x+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 9000).tuple, a=1)

    draw_aura()
    draw_details(x, y)
    draw_extra(-x, y)


def glyph(index: int, x: float, y: float, w: float, h: float):
    BaseSkin.ex_labels[index].draw(Rect(l=x-w/2, r=x+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 9001).tuple, a=1)


def digits(value: int, count: int, x: float, y: float, h: float):
    w = h * 0.48
    for i in range(count):
        digit = value % 10
        dx = x + (count / 2 - i - 0.5) * w
        if i == 0 or value > 0 or count == 2:
            BaseSkin.ex_digits[digit].draw(Rect(l=dx-w/2, r=dx+w/2, b=y-h/2, t=y+h/2).as_quad(), z=get_z_alt(layers.overlay, 9002).tuple, a=1)
        value = value // 10


def draw_details(x: float, y: float):
    h = Layout.field_h
    total = M.ex_perfect + M.ex_great + M.ex_good + M.ex_miss
    if Options.ex_accuracy_enabled:
        accuracy = 10000
        if total > 0:
            accuracy = int((M.ex_perfect + 0.7*M.ex_great + 0.5*M.ex_good)*10000/total + 0.5)
        yy = y - h*0.105
        digits(accuracy//100, 3, x-h*0.036, yy, h*0.035)
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
            digits(value, 4, x+h*0.065, yy, h*0.040)
    if Options.ex_status_enabled and total > 0:
        status_scale = 1.0
        if M.ex_perfect == total:
            glyph(8, -x, y-h*0.105, h*0.22*status_scale, h*0.04*status_scale)
        elif M.ex_miss == 0 and M.ex_good == 0:
            glyph(9, -x, y-h*0.105, h*0.22*status_scale, h*0.04*status_scale)
    if Options.ex_timing_enabled and (not is_watch() or is_replay()) and time()-M.ex_last_hit < 0.65:
        yy = -h*0.17
        if M.ex_error_ms < 0:
            glyph(6, -h*0.085, yy, h*0.09, h*0.035)
        elif M.ex_error_ms > 0:
            glyph(7, -h*0.085, yy, h*0.09, h*0.035)
        digits(int(abs(M.ex_error_ms)+0.5), 3, h*0.015, yy, h*0.035)
        glyph(10, h*0.07, yy, h*0.04, h*0.035)



def draw_extra(x: float, y: float):
    h = Layout.field_h
    z = get_z_alt(layers.overlay, 8998).tuple
    if Options.ex_metrics_enabled:
        fraction = max(0.0, min(1.0, M.ex_display_life / max(1, M.ex_max_life)))
        left = x-h*0.14
        right = x+h*0.14
        yy = y-h*0.19
        BaseSkin.lane_background_black.draw(Rect(l=left,r=right,b=yy-h*0.012,t=yy+h*0.012).as_quad(), z=z, a=0.8)
        if fraction > 0:
            q = Rect(l=left,r=left+(right-left)*fraction,b=yy-h*0.012,t=yy+h*0.012).as_quad()
            if fraction > 0.5:
                BaseSkin.ex_aura[12].draw(q,z=z,a=1)
            elif fraction > 0.2:
                BaseSkin.ex_aura[13].draw(q,z=z,a=1)
            else:
                BaseSkin.ex_aura[14].draw(q,z=z,a=1)
        glyph(12, x-h*0.075, yy-h*0.045, h*0.09, h*0.028)
        digits(M.ex_life, 5, x+h*0.045, yy-h*0.045, h*0.038)
        score = int(1000000*(M.ex_perfect+0.7*M.ex_great+0.5*M.ex_good)/max(1,M.ex_note_total)+0.5)
        glyph(13, x, yy-h*0.087, h*0.10, h*0.027)
        digits(score, 7, x, yy-h*0.13, h*0.045)
    if Options.ex_metrics_enabled and M.ex_life <= M.ex_max_life * 0.2:
        bounds = screen()
        depth = bounds.h * 0.035
        pulse = 0.16 + 0.22 * abs((time() % 0.9) / 0.45 - 1)
        BaseSkin.ex_aura[14].draw(Rect(l=bounds.l,r=bounds.l+depth,b=bounds.b,t=bounds.t).as_quad(),z=z,a=pulse)
        BaseSkin.ex_aura[14].draw(Rect(l=bounds.r-depth,r=bounds.r,b=bounds.b,t=bounds.t).as_quad(),z=z,a=pulse)
    if Options.ex_progress_enabled and not is_watch() and M.ex_end_time > 0:
        fraction = max(0.0,min(1.0,time()/M.ex_end_time))
        yy = safe_area().t-h*0.04
        left = -h*0.35
        right = h*0.35
        BaseSkin.lane_background_black.draw(Rect(l=left,r=right,b=yy-h*0.006,t=yy+h*0.006).as_quad(),z=z,a=0.8)
        if fraction > 0:
            BaseSkin.ex_aura[15].draw(Rect(l=left,r=left+(right-left)*fraction,b=yy-h*0.006,t=yy+h*0.006).as_quad(),z=z,a=1)


def draw_aura():
    if not Options.ex_aura_enabled or M.ex_aura_level < 0.001:
        return
    bounds = screen()
    growth = M.ex_aura_level
    elapsed = time() - M.ex_milestone_time
    pulse = 0.0
    if M.ex_milestone > 0 and elapsed >= 0 and elapsed < 0.8:
        pulse = (1 - elapsed / 0.8) * 0.18
        if M.ex_milestone % 500 == 0:
            pulse *= 1.5
    breath = 0.88 + 0.12 * abs((time() % 2.4) / 1.2 - 1)
    alpha = min(1.0, (0.82 * growth + pulse) * breath * Options.ex_aura_intensity)
    depth = bounds.h * (0.025 + 0.085 * growth + pulse * 0.08)
    z = get_z_alt(layers.overlay, 8997).tuple
    for group in range(3):
        weight = max(0.0, 1-M.ex_aura_ap-M.ex_aura_fc)
        if group == 0:
            weight = M.ex_aura_ap
        elif group == 1:
            weight = M.ex_aura_fc
        a = alpha * weight
        if a > 0.001:
            index = group * 4
            BaseSkin.ex_aura[index].draw(Rect(l=bounds.l,r=bounds.r,b=bounds.t-depth,t=bounds.t).as_quad(),z=z,a=a)
            BaseSkin.ex_aura[index+1].draw(Rect(l=bounds.l,r=bounds.r,b=bounds.b,t=bounds.b+depth).as_quad(),z=z,a=a)
            BaseSkin.ex_aura[index+2].draw(Rect(l=bounds.l,r=bounds.l+depth,b=bounds.b,t=bounds.t).as_quad(),z=z,a=a)
            BaseSkin.ex_aura[index+3].draw(Rect(l=bounds.r-depth,r=bounds.r,b=bounds.b,t=bounds.t).as_quad(),z=z,a=a)
