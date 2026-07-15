"""Qwen3.5 gradient-flow + toy-training smoke test.

Validates the Qwen3.5 CausalLM-routing patch (verl/utils/model.py) and, crucially,
that gradients flow through the WHOLE hybrid model — including the Gated-DeltaNet
(``linear_attn``) layers — and that an optimizer step actually changes the weights by
overfitting a tiny fixed toy batch.

Uses standard padded batches (NOT packed/varlen), which is the GDN-safe path
(see verl #6549: packed sequences trigger the torch_chunk_gated_delta_rule IMA).

Run on 1 GPU, e.g.:
  FLA_TILELANG=0 PYTHONPATH=$PWD python scripts/smoke_qwen35_gradflow.py \
      --model /path/to/Qwen3.5-0.8B --steps 12
"""

import argparse

import torch


def group_of(name):
    if "linear_attn" in name:
        return "linear_attn(GDN)"
    if "self_attn" in name:
        return "self_attn"
    if ".mlp." in name or name.endswith(".mlp"):
        return "mlp"
    if "visual" in name or "vision" in name:
        return "vision(unused)"
    return "embed/other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="HF id or local snapshot path")
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--seqlen", type=int, default=48)
    ap.add_argument("--bsz", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--attn", default="sdpa")
    args = ap.parse_args()

    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

    from verl.utils.model import get_hf_auto_model_class

    # --- 1. routing patch check ---
    cfg = AutoConfig.from_pretrained(args.model, trust_remote_code=False)
    auto_cls = get_hf_auto_model_class(cfg)
    print(f"[routing] model_type={getattr(cfg, 'model_type', None)} arch={cfg.architectures} "
          f"-> {auto_cls.__name__}")
    assert auto_cls is AutoModelForCausalLM, (
        f"routing patch failed: expected AutoModelForCausalLM, got {auto_cls.__name__}")

    # --- 2. load model as causal text LM ---
    dtype = getattr(torch, args.dtype)
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=False)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = auto_cls.from_pretrained(
        args.model, dtype=dtype, config=cfg, trust_remote_code=False,
        attn_implementation=args.attn,
    ).cuda()
    model.train()
    model.config.use_cache = False

    # --- 3. param groups ---
    groups = {}
    for n, p in model.named_parameters():
        if p.requires_grad:
            groups.setdefault(group_of(n), []).append((n, p))
    print("[params] trainable groups:", {k: len(v) for k, v in groups.items()})

    # --- 4. toy batch: overfit a fixed sentence (labels = shifted input) ---
    text = "The three professors reached a consensus to admit student number two."
    enc = tok([text] * args.bsz, return_tensors="pt", padding="max_length",
              truncation=True, max_length=args.seqlen)
    input_ids = enc["input_ids"].cuda()
    attn = enc["attention_mask"].cuda()
    labels = input_ids.clone()
    labels[attn == 0] = -100

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)

    # full snapshot (to CPU, fp32) so we can measure weight change across ALL params per group
    before = {n: p.detach().float().cpu().clone() for n, p in model.named_parameters() if p.requires_grad}

    gradnorm0 = {}
    gradcount0 = {}
    losses = []
    for step in range(args.steps):
        opt.zero_grad(set_to_none=True)
        out = model(input_ids=input_ids, attention_mask=attn, labels=labels)
        loss = out.loss
        loss.backward()
        if step == 0:
            for g, ps in groups.items():
                gn = sum(p.grad.detach().float().norm().item() for _, p in ps if p.grad is not None)
                nz = sum(1 for _, p in ps if p.grad is not None and p.grad.detach().abs().sum() > 0)
                gradnorm0[g] = gn
                gradcount0[g] = (nz, len(ps))
        opt.step()
        losses.append(float(loss.item()))
        print(f"[step {step:2d}] loss={loss.item():.4f}")

    named = dict(model.named_parameters())
    print("\n[gradflow] per-group grad-norm @ step 0  (params with nonzero grad / total):")
    for g in groups:
        nz, tot = gradcount0[g]
        print(f"   {g:20s} grad_norm={gradnorm0[g]:.4e}   nonzero_grad={nz}/{tot}")

    # per-group weight change across ALL params
    print(f"\n[weightchange] per-group after {args.steps} steps (lr={args.lr}):")
    wchg = {}
    for g, ps in groups.items():
        gmax = 0.0
        nchg = 0
        for n, _ in ps:
            d = (named[n].detach().float().cpu() - before[n]).abs().max().item()
            gmax = max(gmax, d)
            if d > 0:
                nchg += 1
        wchg[g] = gmax
        print(f"   {g:20s} max|Δ|={gmax:.3e}   changed={nchg}/{len(ps)}")

    core = ["linear_attn(GDN)", "self_attn", "mlp"]
    ok_grad = all(gradnorm0.get(g, 0) > 0 for g in core if g in groups)
    ok_wchg = all(wchg.get(g, 0) > 0 for g in core if g in groups)
    ok_loss = losses[-1] < losses[0]
    print(f"\nRESULT grad_flows_core_groups={ok_grad} "
          f"loss_decreased={ok_loss} ({losses[0]:.3f}->{losses[-1]:.3f}) "
          f"weights_changed_core={ok_wchg}")
    print("SMOKE_OK" if (ok_grad and ok_wchg and ok_loss) else "SMOKE_FAIL")


if __name__ == "__main__":
    main()
