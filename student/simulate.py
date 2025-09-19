import json, random

def simulate_lane(law, style, history_path):
    """
    Tiny synthetic simulator:
    - Lower smoothing/forgiveness can reduce flapping but slow recovery.
    - Higher forgiveness can reduce reds but may raise false-green if too high.
    - VKD closer to 1.0 chases short wins → more flapping.
    Outputs summary metrics used by the judge.
    """

    base_noise = 0.03
    forgiveness = style["forgiveness"]
    smoothing   = style["smoothing"]
    vkd         = style["vkd_discount"]

    # heuristics → [0,1]
    false_green = max(0.0, 0.02 + (forgiveness - 0.12)*0.25 + (1.0 - smoothing)*0.05 + base_noise*random.random())
    flap_index  = max(0.0, 0.06 + (0.30 - smoothing)*0.20 + (1.0 - vkd)*(-0.05) + base_noise*random.random())
    # lower halflife is better (faster recovery). More smoothing usually slows recovery a bit, forgiveness helps.
    recovery_halflife = max(1, int(2 + (smoothing*4) - (forgiveness*3) + (0.5 - vkd)*1.5 + random.random()))
    exception_rate = max(0.0, 0.01 + (forgiveness - 0.10)*0.10 + base_noise*random.random())
    # clamp
    false_green = min(false_green, 0.20)
    flap_index  = min(flap_index,  0.40)
    exception_rate = min(exception_rate, 0.20)

    return {
        "false_green": round(false_green, 3),
        "flap_index": round(flap_index, 3),
        "recovery_halflife": int(recovery_halflife),
        "exception_rate": round(exception_rate, 3)
    }
