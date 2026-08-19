---
marp: true
theme: default
paginate: true
size: 16:9
title: Longer critic warmup — matched privileged vs. vanilla results
description: Results from the asymmetric-critic warmup-30 experiments
style: |
  section {
    font-family: Helvetica, Arial, ui-sans-serif, sans-serif;
    background: #ffffff;
    color: #111111;
    padding: 56px 68px;
    font-size: 27px;
  }
  section::after {
    color: #777777;
    font-size: 16px;
  }
  header, footer {
    color: #777777;
    font-size: 15px;
  }
  h1 {
    color: #000000;
    font-size: 48px;
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.035em;
    margin: 0 0 30px;
  }
  h2 {
    color: #111111;
    font-size: 35px;
    line-height: 1.1;
    margin: 0 0 22px;
  }
  strong { color: #000000; font-weight: 750; }
  a { color: #000000; text-decoration: underline; }
  ul, ol { margin-top: 12px; }
  li { margin: 10px 0; }
  table {
    width: 100%;
    font-size: 21px;
    border-collapse: collapse;
  }
  th {
    background: #eeeeee;
    color: #000000;
  }
  td, th {
    padding: 10px 12px;
    border: 1px solid #bdbdbd;
  }
  blockquote {
    border-left: 4px solid #000000;
    color: #111111;
    background: #f5f5f5;
    padding: 12px 22px;
    margin: 20px 0;
  }
  .lead {
    background: #000000;
    color: #ffffff;
    text-align: left;
  }
  .lead h1 {
    color: #ffffff;
    font-size: 62px;
    max-width: 980px;
  }
  .lead h2 { color: #ffffff; font-weight: 400; }
  .lead footer, .lead::after { color: #aaaaaa; }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
    align-items: start;
  }
  .big-number {
    color: #000000;
    font-size: 64px;
    font-weight: 800;
    line-height: 1;
  }
  .label {
    color: #555555;
    font-size: 21px;
    margin-top: 8px;
  }
  .verdict {
    color: #000000;
    font-size: 32px;
    font-weight: 700;
    border-bottom: 2px solid #000000;
    padding-bottom: 10px;
    margin-bottom: 18px;
  }
  .caution { color: #000000; }
  .small { color: #666666; font-size: 17px; }
  .source { color: #666666; font-size: 14px; }
  section.compact { font-size: 23px; }
  section.compact h1 { font-size: 44px; margin-bottom: 20px; }
  section.compact h2 { font-size: 31px; margin-bottom: 14px; }
  section.compact li { margin: 7px 0; }
  section.compact pre { margin: 10px 0; }
  .design-flow {
    display: grid;
    grid-template-columns: 1fr 90px 1fr;
    align-items: center;
    margin: 38px 0 30px;
  }
  .design-flow .stage {
    border-top: 2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 24px 6px;
  }
  .design-flow .arrow {
    text-align: center;
    font-size: 42px;
    font-weight: 300;
  }
  .design-flow .eyebrow {
    color: #666666;
    font-size: 16px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .contrast {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 56px;
    border-top: 1px solid #999999;
    padding-top: 22px;
  }
  .contrast h2 { margin-bottom: 8px; }
  .metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 48px;
    margin: 52px 0 42px;
  }
  .metrics.two { grid-template-columns: repeat(2, 1fr); }
  .metric {
    border-top: 2px solid #000000;
    padding-top: 18px;
  }
  .metric .value {
    font-size: 58px;
    font-weight: 750;
    line-height: 1;
    margin-bottom: 10px;
  }
  .metric .pair {
    font-size: 36px;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 12px;
  }
  .curve {
    display: block;
    width: 100%;
    max-height: 450px;
    object-fit: contain;
  }
  .overlap-plot {
    display: block;
    width: 100%;
    max-height: 390px;
    object-fit: contain;
    margin: 6px 0 12px;
  }
  .equation {
    font-family: "SFMono-Regular", Consolas, monospace;
    font-size: 27px;
    line-height: 1.4;
    border-top: 2px solid #000000;
    border-bottom: 2px solid #000000;
    padding: 18px 0;
    margin: 26px 0;
  }
  section.limit h1 { font-size: 40px; }
  section.limit .equation {
    font-size: 24px;
    padding: 10px 0;
    margin: 12px 0;
  }
  section.limit .references { font-size: 12px; }
  .pitch-flow {
    display: grid;
    grid-template-columns: 1fr 48px 1.2fr 48px 1.15fr;
    align-items: center;
    margin: 46px 0 34px;
  }
  .pitch-flow .stage {
    border-top: 2px solid #000000;
    border-bottom: 2px solid #000000;
    min-height: 150px;
    padding: 22px 4px;
  }
  .pitch-flow .arrow {
    text-align: center;
    font-size: 34px;
  }
  .pitch-flow .eyebrow {
    color: #666666;
    font-size: 15px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }
  .references {
    color: #555555;
    font-size: 14px;
    line-height: 1.45;
  }
---

<!-- _class: lead -->

# Longer critic warmup resolves the fit problem

## …but privileged information does not yield a clear policy advantage

Matched actor-compute experiments · Qwen3-4B · 95 training steps

---

# Executive result

<div class="columns">
<div>

<div class="verdict">Warmup: supported</div>

Both critics reached approximately **0.50 explained variance by step 30** and approximately **0.72–0.78 median EV late in joint training**.

</div>
<div>

<div class="verdict caution">Actor effect: mixed</div>

Privileged ends higher on social-optimal choice rate. Vanilla ends higher on consensus and welfare efficiency.

</div>
</div>

> Warmup solved the critic optimization problem. Better critic information did not translate into a broad policy-quality gain.

---

# Three questions organize the experiment

1. **Can the critic learn?** — longer warmup should produce stable fit through joint training.

2. **Does privileged information improve value prediction?** — privileged should outperform vanilla.

3. **Does a privileged critic improve the actor?** — social outcomes should improve consistently.

> Critic fit and policy quality are separate outcomes.

---

# Only the critic’s input changed

<div class="design-flow">
<div class="stage">
<div class="eyebrow">Policy side — identical</div>

Actor-visible prompt → sampled response

</div>
<div class="arrow">→</div>
<div class="stage">
<div class="eyebrow">Critic side — treatment</div>

Evaluate the same response with one of two prompts

</div>
</div>

<div class="contrast">
<div>

## Vanilla

Exact actor-visible prompt

</div>
<div>

## Privileged

Same prompt + all utilities  
<span class="small">approximately 174 additional tokens</span>

</div>
</div>

<span class="small">Held fixed: Qwen3-4B · 30 critic-only steps · 65 joint steps · same rewards, actor compute, and commit</span>

---

# At the end of warmup, privileged and vanilla were tied

<div class="metrics two">
<div class="metric">
<div class="value">0.501</div>
<div>Privileged</div>
</div>
<div class="metric">
<div class="value">0.498</div>
<div>Vanilla</div>
</div>
</div>

> After 30 warmup steps, all critics reached approximately **0.50 explained variance**. The privileged input showed no advantage at this boundary.

---

# Strong critic fit persisted during joint training

| Run | End of warmup | Late joint median | Peak EV |
|---|---:|---:|---:|
| Privileged | 0.501 | **0.748** | 0.847 |
| Vanilla | 0.498 | 0.721 | 0.861 |

> Joint training did not destroy critic fit. The late-median difference was only **0.027**, so single-checkpoint comparisons are not reliable.

---

# Actor outcomes improved in different ways

<img class="curve" src="critic_actor_curves.png" alt="Seven-step rolling mean of social-optimal rate and social-welfare efficiency" />

<span class="small">Seven-step trailing mean · actor updates after step 30 · late medians: social optimal 57% vs. 52%; welfare 87% vs. 93%</span>

---

# Actor outcomes differ by objective

| Outcome | Meaning | Privileged | Vanilla |
|---|---|---:|---:|
| **Social-optimal choice rate** | Selected the student with the highest total utility | **53.1%** | 46.9% |
| **Consensus rate** | All professors agreed on the final student | 93.8% | **100%** |
| **Welfare efficiency** | Achieved total utility ÷ maximum possible utility | 88.5% | **93.4%** |

> Privileged chose the exact social optimum more often. Vanilla reached agreement more reliably and captured more of the available total utility.

---

# Takeaway

## Longer warmup solved critic fit

Both critics reached approximately **0.50 explained variance** after warmup and retained strong fit during joint training.

## Actor effects were mixed

Privileged produced a higher social-optimal choice rate. Vanilla produced higher consensus and welfare efficiency.

> **Privileged critic information changed which outcomes improved, but did not produce a clear overall policy advantage.**

---

<!-- _class: compact -->

# Turn an expert trace into valid Qwen training data

<div class="columns">
<div>

## 1. Generate reachable candidates

- Run Haiku and Qwen from the **same prompt and environment state**.
- Keep the verified high-reward Haiku trajectory as the target.
- Sample (K) trajectories from the frozen old Qwen policy and save their rollout log-probabilities.

</div>
<div>

## 2. Learn from the best projection

- Rank Qwen candidates by:  
  `reward − β × distance to Haiku`
- Update Qwen with PPO on the selected **Qwen-generated** trajectories.
- If no candidate clears a reward threshold, use bounded Haiku SFT as a separate fallback loss.

</div>
</div>

> **Haiku supplies the direction; Qwen supplies the trajectory that makes the policy gradient valid.**

<div class="references">
<strong>Theoretical basis:</strong> nearest-sample projection — Li & Malik, <a href="https://arxiv.org/abs/1809.09087">IMLE</a> (2018) · clipped updates on policy-generated trajectories — Schulman et al., <a href="https://arxiv.org/abs/1707.06347">PPO</a> (2017)
</div>

---

<!-- _class: compact -->

# SFT makes nearest-sample imitation usable

<img class="overlap-plot" src="imle_overlap_normals.png" alt="Normal distributions illustrating little policy-expert overlap before SFT and substantially more overlap after SFT" />

<div class="columns">
<div>

**Finite candidate budget:** if Qwen assigns negligible mass near an expert trace, none of its sampled candidates will be a meaningful projection.

</div>
<div>

**After SFT warmup:** expert-like candidates become reachable, so reward and distance can select useful Qwen trajectories for PPO.

</div>
</div>

<div class="small"><strong>Finite-sample intuition:</strong> E[d<sub>min</sub>(z<sub>E</sub>)] ∝ [K p<sub>θ</sub>(z<sub>E</sub>)]<sup>−1/d</sup>. The useful signal is policy density around expert data.</div>

---

<!-- _class: compact limit -->

# Infinite samples recover expert MLE on shared support

For expert trajectory y<sub>E</sub>, sample K candidates from old Qwen and keep the nearest:

<div class="equation">
ŷ<sub>K</sub> = arg min<sub>yᵢ ∼ π<sub>old</sub></sub> d(yᵢ, y<sub>E</sub>)
</div>

If Qwen gives that discrete trajectory non-zero probability,

<div class="equation">
P(ŷ<sub>K</sub> = y<sub>E</sub>) = 1 − (1 − π<sub>old</sub>(y<sub>E</sub> | x))<sup>K</sup> → 1
</div>

The projected imitation loss therefore converges to expert SFT/MLE:

<div class="equation">
−log π<sub>θ</sub>(ŷ<sub>K</sub> | x) → −log π<sub>θ</sub>(y<sub>E</sub> | x)
</div>

> SFT warmup raises practical overlap. Wulfmeier et al. stabilize LLM GAIL by starting from an MLE-trained checkpoint and retaining MLE terms during sequential imitation.

<div class="references">
<strong>References:</strong> Li & Malik, <a href="https://arxiv.org/abs/1809.09087">Implicit Maximum Likelihood Estimation</a> (2018) · Ho & Ermon, <a href="https://arxiv.org/abs/1606.03476">Generative Adversarial Imitation Learning</a> (2016) · Wulfmeier et al., <a href="https://arxiv.org/abs/2409.01369">Imitating Language via Scalable Inverse Reinforcement Learning</a> (NeurIPS 2024)
</div>
