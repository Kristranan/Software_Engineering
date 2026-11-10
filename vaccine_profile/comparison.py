def compare_exposure(heat_s, freeze_s, profile):
    heat_exceeded = heat_s > profile["heat_limit_s"]
    freeze_exceeded = freeze_s > profile["freeze_limit_s"]

    return {
        "heat_exceeded": heat_exceeded,
        "freeze_exceeded": freeze_exceeded,
    }

