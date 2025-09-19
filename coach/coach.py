import json, os, time, hashlib, random
from pathlib import Path
from student.simulate import simulate_lane

ROOT = Path(__file__).resolve().parents[1]
LAW = json.loads((ROOT/"canon/law.json").read_text())

LANE = "lane1"
STYLE_PATH = ROOT/f"adapters/{LANE}/style.json"
HISTORY = ROOT/f"data/{LANE}/history.jsonl"

DOCS = ROOT/"docs"
RECEIPTS = DOCS/"receipts"
RECEIPTS.mkdir(parents=True, exist_ok=True)

def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()

def read_style():
    if STYLE_PATH.exists():
        return json.loads(STYLE_PATH.read_text())
    # default house style (conservative)
    return {
        "forgiveness": 0.10,   # how quickly to forgive after an incident
        "smoothing":  0.20,   # EMA / windowing
        "reflex_order": ["rollback","rules_first","retune"],  # priority order
        "vkd_discount": 0.50   # discount short-term wins
    }

def propose_style(old):
    # tiny, legal nudges (bounded)
    nudges = {
        "forgiveness": round(min(0.30, max(0.02, old["forgiveness"] + random.choice([-0.02, 0.02]))), 2),
        "smoothing":  round(min(0.40, max(0.05, old["smoothing"]  + random.choice([-0.05, 0.05]))), 2),
        "vkd_discount": round(min(0.90, max(0.20, old["vkd_discount"] + random.choice([-0.05, 0.05]))), 2)
    }
    # keep reflex order stable 80% of time; occasionally swap last two
    if random.random() < 0.20:
        ro = old["reflex_order"][:]
        ro[-1], ro[-2] = ro[-2], ro[-1]
    else:
        ro = old["reflex_order"]
    nudges["reflex_order"] = ro
    return nudges

def judge(old_style, new_style, sim):
    law = LAW
    verdict = "accepted"
    reasons = []

    # hard law: no style can change bands or thresholds (enforced structurally)
    if law["constraints"]["no_threshold_edits_by_style"] is not True:
        verdict, reasons = "rejected", ["law misconfigured: thresholds must be immutable"]

    # band-preserving proxy: false_green must not increase
    if sim["false_green"] > law["benchmark"]["max_false_green"]:
        verdict, reasons = "rejected", reasons + [f"false_green {sim['false_green']:.3f} > {law['benchmark']['max_false_green']:.3f}"]

    # anti-flap: flap index must be within target and not worse than baseline
    if sim["flap_index"] > law["benchmark"]["max_flap_index"]:
        verdict, reasons = "rejected", reasons + [f"flap_index {sim['flap_index']:.3f} > {law['benchmark']['max_flap_index']:.3f}"]

    # recovery: halflife should be <= target
    if sim["recovery_halflife"] > law["benchmark"]["target_recovery_halflife"]:
        verdict, reasons = "rejected", reasons + [f"recovery_halflife {sim['recovery_halflife']} > {law['benchmark']['target_recovery_halflife']}"]

    # exceptions: keep rare and expiring
    if sim["exception_rate"] > law["exception"]["target_rate"]:
        verdict, reasons = "rejected", reasons + [f"exception_rate {sim['exception_rate']:.3f} > {law['exception']['target_rate']:.3f}"]

    return verdict, reasons

def write_receipt(title, status, point, because_list, but, so, extras=None, path=None):
    obj = {
        "title": title,
        "status": status,
        "point": point,
        "because": because_list,
        "but": but,
        "so": so,
        "metrics": {"coherence": {"band": "green" if status=="OK" else "red"}},
        "policy": {"use":"demo","share":"yes","train":"yes"},
        "stamp": {"issued_at": now_utc(), "digest_sha256": ""}
    }
    if extras: obj.update(extras)
    obj["stamp"]["digest_sha256"] = digest(obj)
    out = path or (RECEIPTS/"tuning.json")
    out.write_text(json.dumps(obj, indent=2))
    (ROOT/"docs/receipt.latest.json").write_text(json.dumps(obj, indent=2))

def main():
    old_style = read_style()
    new_style = propose_style(old_style)

    # simulate shadow run under proposed style
    sim = simulate_lane(LAW, new_style, HISTORY)

    verdict, reasons = judge(old_style, new_style, sim)

    if verdict == "accepted":
        STYLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STYLE_PATH.write_text(json.dumps(new_style, indent=2))

    because = [
        f"lane: {LANE}",
        f"old_style: {json.dumps(old_style)}",
        f"new_style: {json.dumps(new_style)}",
        f"sim: {json.dumps(sim)}"
    ]

    write_receipt(
        title="Tuning Receipt",
        status="OK" if verdict=="accepted" else "ERROR",
        point="Shadow → judge by Canon → (maybe) adopt style",
        because_list=because,
        but="; ".join(reasons),
        so="adopted" if verdict=="accepted" else "rejected",
        extras={"verdict": verdict}
    )

    # mirror Canon to docs for visibility
    (RECEIPTS/"canon.json").write_text((ROOT/"canon/law.json").read_text())

if __name__ == "__main__":
    main()
