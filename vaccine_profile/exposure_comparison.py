from exposure.heat_exposure.heat_exposure import heat_increment_s
from exposure.freeze_exposure import accumulate_freeze
from comparison import compare_exposure


def update_and_compare(
    state, record, profile, upper_limit_c, lower_limit_c
):
    if state is None:
        state = {
            "heat_s": 0,
            "freeze_s": 0,
            "last_good": None,
        }

    heat_s = state["heat_s"] + heat_increment_s(
        state["last_good"], record, upper_limit_c
    )

    freeze_state = accumulate_freeze(
        {
            "freeze_s": state["freeze_s"],
            "last_good": state["last_good"],
        },
        record,
        lower_limit_c,
    )

    new_state = {
        "heat_s": heat_s,
        "freeze_s": freeze_state["freeze_s"],
        "last_good": freeze_state["last_good"],
    }

    result = compare_exposure(
        new_state["heat_s"], new_state["freeze_s"], profile
    )

    return new_state, result