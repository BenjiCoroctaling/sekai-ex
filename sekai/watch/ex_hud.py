from sonolus.script.archetype import EntityRef
from sonolus.script.bucket import Judgment
from sonolus.script.runtime import is_replay, time
from sekai.play.common import PlayLevelMemory as M
from sekai.play.ex_hud import update_rank, miss_cost
from sekai.watch.note import WatchBaseNote


from sekai.watch.ex_hud_data import WatchHudData


def update_watch_hud():
    now = time()
    M.ex_life = M.ex_max_life
    M.ex_perfect = 0
    M.ex_great = 0
    M.ex_good = 0
    M.ex_miss = 0
    M.ex_last_hit = -1e8
    M.ex_error_ms = 0
    index = WatchHudData.head
    while index > 0:
        note = EntityRef[WatchBaseNote](index=index).get()
        hit_time = note.target_time
        if is_replay():
            hit_time = note.end_time
            if hit_time == 0 and note.accuracy == 0 and note.judgment == Judgment.MISS:
                hit_time = 1e8
        if hit_time <= now:
            if note.judgment == Judgment.PERFECT:
                M.ex_perfect += 1
            elif note.judgment == Judgment.GREAT:
                M.ex_great += 1
            elif note.judgment == Judgment.GOOD:
                M.ex_good += 1
            elif note.judgment == Judgment.MISS:
                M.ex_miss += 1
                M.ex_life = max(0, M.ex_life - miss_cost(note.kind))
            if is_replay() and hit_time >= M.ex_last_hit:
                M.ex_last_hit = hit_time
                M.ex_error_ms = note.accuracy * 1000
                if note.judgment == Judgment.MISS:
                    M.ex_error_ms = 0
        index = note.ex_hud_next
    if M.ex_miss == 0 and M.ex_good == 0:
        M.ex_combo = M.ex_perfect + M.ex_great
    else:
        M.ex_combo = 0
    update_rank()
