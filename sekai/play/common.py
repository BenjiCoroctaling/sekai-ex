from sonolus.script.globals import level_memory


@level_memory
class PlayLevelMemory:
    last_note_sfx_time: float
    ex_perfect: int
    ex_great: int
    ex_good: int
    ex_miss: int
    ex_error_ms: float
    ex_combo: int
    ex_last_hit: float
    ex_rank: int
    ex_rank_changed: float


def init_play_common():
    PlayLevelMemory.last_note_sfx_time = -1e8

    PlayLevelMemory.ex_perfect = 0
    PlayLevelMemory.ex_great = 0
    PlayLevelMemory.ex_good = 0
    PlayLevelMemory.ex_miss = 0
    PlayLevelMemory.ex_error_ms = 0
    PlayLevelMemory.ex_combo = 0
    PlayLevelMemory.ex_last_hit = -100
    PlayLevelMemory.ex_rank = 8
    PlayLevelMemory.ex_rank_changed = -100
