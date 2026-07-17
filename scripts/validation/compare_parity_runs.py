#!/usr/bin/env python3
"""Tier-2 numerical comparison: port (verl-0.8) vs old branch (verl-0.6), dense Qwen3-4B.

Pulls both runs from wandb project `verl_parity_qwen3_4b`, aligns by training step,
and reports a per-metric similar/better/worse verdict plus numerical-stability flags.

Because dual-GAE and env-reward are proven numerically identical (see
tests/trainer/ppo/test_dual_gae_parity_cpu.py and scripts/validation/run_env_reward_parity.sh),
any divergence here is attributable to the STACK (verl 0.6->0.8, vLLM, FSDP, packing),
not the credit-assignment math.

Usage:
  python compare_parity_runs.py                       # auto-find latest old_/port_ runs
  python compare_parity_runs.py --old NAME --port NAME
  ENTITY / PROJECT overridable via flags.
"""
import argparse
import math

ENTITY_DEFAULT = "aseo-carnegie-mellon-university"
PROJECT_DEFAULT = "verl_parity_qwen3_4b"

# metric -> (candidate keys across verl versions, higher_is_better or None for "closeness only")
METRICS = {
    "reward/score_mean":   (["critic/score/mean", "critic/rewards/mean"], True),
    "actor/entropy":       (["actor/entropy", "actor/entropy_loss"], None),
    "actor/pg_loss":       (["actor/pg_loss"], None),
    "actor/grad_norm":     (["actor/grad_norm"], None),
    "actor/kl":            (["actor/kl_loss", "actor/kl", "actor/ppo_kl"], None),
    "critic/vf_loss":      (["critic/vf_loss"], None),
    "critic/grad_norm":    (["critic/grad_norm"], None),
    "adv/mean":            (["critic/advantages/mean"], None),
    "adv/std":             (["critic/advantages/std"], None),
    "returns/mean":        (["critic/returns/mean"], None),
    "values/mean":         (["critic/values/mean", "critic/vpred_mean"], None),
    "env/consensus":       (["env/negotiation/consensus_reached", "episodes_consensus",
                             "env/episodes_consensus"], True),
    "env/social_welfare":  (["env/social_welfare/efficiency", "socially_optimal_rate",
                             "env/socially_optimal_rate"], True),
}


def _find_key(df_cols, candidates):
    for c in candidates:
        if c in df_cols:
            return c
    # suffix match fallback
    for c in candidates:
        tail = c.split("/")[-1]
        for col in df_cols:
            if col.endswith("/" + tail) or col == tail:
                return col
    return None


def _series(hist, candidates):
    key = _find_key(hist.columns, candidates)
    if key is None:
        return None, None
    s = hist[key].dropna()
    return (s if len(s) else None), key


def _last_mean(s, k=5):
    if s is None or len(s) == 0:
        return None, None
    tail = s.iloc[-k:]
    return float(s.iloc[-1]), float(tail.mean())


def _has_nonfinite(hist):
    bad = {}
    for col in hist.columns:
        try:
            vals = hist[col].dropna().values
        except Exception:
            continue
        n = sum(1 for v in vals if isinstance(v, (int, float)) and not math.isfinite(v))
        if n:
            bad[col] = n
    return bad


def _pick_run(api, entity, project, prefix, explicit):
    try:
        runs = list(api.runs(f"{entity}/{project}"))
    except (ValueError, TypeError, KeyError):
        return None  # project not created yet (no runs have logged)
    if explicit:
        for r in runs:
            if r.name == explicit:
                return r
        raise SystemExit(f"run named {explicit!r} not found in {project}")
    cands = [r for r in runs if (r.name or "").startswith(prefix)]
    if not cands:
        return None
    # newest by created_at
    cands.sort(key=lambda r: r.created_at, reverse=True)
    return cands[0]


def main():
    import wandb
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", default=ENTITY_DEFAULT)
    ap.add_argument("--project", default=PROJECT_DEFAULT)
    ap.add_argument("--old", default=None, help="old-branch run display name (default: latest old_*)")
    ap.add_argument("--port", default=None, help="port run display name (default: latest port_*)")
    args = ap.parse_args()

    api = wandb.Api()
    old = _pick_run(api, args.entity, args.project, "old_dense4b", args.old)
    port = _pick_run(api, args.entity, args.project, "port_dense4b", args.port)
    if old is None or port is None:
        print(f"waiting for runs — old={old and old.name} port={port and port.name} "
              f"(project {args.project})")
        return

    print(f"OLD  (verl-0.6): {old.name}   state={old.state}   step={old.summary.get('training/global_step','?')}")
    print(f"PORT (verl-0.8): {port.name}  state={port.state}  step={port.summary.get('training/global_step','?')}")
    print("=" * 92)

    ho = old.history(samples=100000, pandas=True)
    hp = port.history(samples=100000, pandas=True)

    hdr = f"{'metric':22} | {'OLD last':>12} {'(mean5)':>10} | {'PORT last':>12} {'(mean5)':>10} | verdict"
    print(hdr); print("-" * len(hdr))
    for label, (cands, hib) in METRICS.items():
        so, ko = _series(ho, cands)
        sp, kp = _series(hp, cands)
        ol, om = _last_mean(so)
        pl, pm = _last_mean(sp)
        if ol is None and pl is None:
            continue
        def fmt(x):
            return "   n/a    " if x is None else f"{x:12.4g}"
        verdict = ""
        if ol is not None and pl is not None:
            if hib is True:
                d = pm - om
                rel = d / (abs(om) + 1e-9)
                verdict = ("PORT better" if rel > 0.05 else "PORT worse" if rel < -0.05 else "~match") + f" ({d:+.3g})"
            else:
                rel = abs(pm - om) / (abs(om) + 1e-9)
                verdict = f"close ({rel*100:.0f}% diff)" if rel < 0.25 else f"DIVERGES ({rel*100:.0f}%)"
        print(f"{label:22} | {fmt(ol)} {fmt(om)} | {fmt(pl)} {fmt(pm)} | {verdict}")

    print("=" * 92)
    for tag, h in (("OLD", ho), ("PORT", hp)):
        bad = _has_nonfinite(h)
        if bad:
            top = ", ".join(f"{k}:{v}" for k, v in list(bad.items())[:6])
            print(f"[{tag}] NON-FINITE values detected (instability): {top}")
        else:
            print(f"[{tag}] no NaN/Inf in any logged metric — numerically stable")


if __name__ == "__main__":
    main()
