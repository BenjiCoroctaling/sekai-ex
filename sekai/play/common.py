from sonolus.script.globals import level_memory


@level_memory
class PlayLevelMemory:
    last_note_sfx_time: float
    ex_perfect: int
    ex_great: int
    ex_good: int
    ex_miss: int
    ex_error_ms: float
    ex_max_life: int
    ex_life: int
    ex_note_total: int
    ex_end_time: float
    ex_milestone: int
    ex_milestone_time: float
    ex_combo: int
    ex_last_hit: float
    ex_rank: int
    ex_rank_changed: float


def init_play_common(initial_life: int):
    PlayLevelMemory.last_note_sfx_time = -1e8

    PlayLevelMemory.ex_perfect = 0
    PlayLevelMemory.ex_great = 0
    PlayLevelMemory.ex_good = 0
    PlayLevelMemory.ex_miss = 0
    PlayLevelMemory.ex_error_ms = 0
    PlayLevelMemory.ex_max_life = max(1, initial_life)
    PlayLevelMemory.ex_life = initial_life
    PlayLevelMemory.ex_note_total = 0
    PlayLevelMemory.ex_end_time = 0
    PlayLevelMemory.ex_milestone = 0
    PlayLevelMemory.ex_milestone_time = -100
    PlayLevelMemory.ex_combo = 0
    PlayLevelMemory.ex_last_hit = -100
    PlayLevelMemory.ex_rank = 8
    PlayLevelMemory.ex_rank_changed = -100
