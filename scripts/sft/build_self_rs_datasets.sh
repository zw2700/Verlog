#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=/zfsauton2/home/frankwu2/unscripted/Verlog
ENV_PATH=${ENV_PATH:-/zfsauton/scratch/cpulling/conda_envs/verlog}
PYTHON_BIN=${PYTHON_BIN:-${ENV_PATH}/bin/python3}
RUN_TAG=${RUN_TAG:-qwen3_self_rs_v1}
OUTPUT_ROOT=${OUTPUT_ROOT:-${PROJECT_DIR}/outputs/sft}
RUN_ROOT=${OUTPUT_ROOT}/${RUN_TAG}
INPUT_JSONL=${INPUT_JSONL:-${RUN_ROOT}/attempts.jsonl}
DATASET_DIR=${DATASET_DIR:-${RUN_ROOT}/dataset_raw}
SWEEP_DATASET_ROOT=${SWEEP_DATASET_ROOT:-${RUN_ROOT}/sweep_datasets_v1}
TARGET_TOKENIZER=${TARGET_TOKENIZER:-Qwen/Qwen3-4B}
SELECTED_SCENARIOS=${SELECTED_SCENARIOS:-351}
VALIDATION_FRACTION=${VALIDATION_FRACTION:-0.1}
SELECTION_SEED=${SELECTION_SEED:-1}
SPLIT_SEED=${SPLIT_SEED:-1}
SUBSET_SEED=${SUBSET_SEED:-1}
MAX_THINK_TOKENS=${MAX_THINK_TOKENS:-64}
HAIKU_SELECTED_EPISODES=${HAIKU_SELECTED_EPISODES:-${PROJECT_DIR}/outputs/sft/haiku_qwen3_pilot/dataset_raw/selected_episodes.jsonl}

if [[ ! -x ${PYTHON_BIN} ]]; then
    echo "Python environment not found: ${PYTHON_BIN}" >&2
    exit 2
fi
if [[ ! -s ${INPUT_JSONL} ]]; then
    echo "Rollout file is missing or empty: ${INPUT_JSONL}" >&2
    exit 2
fi
RAW_DATASET_COMPLETE=false
if [[ -e ${DATASET_DIR} ]]; then
    RAW_DATASET_COMPLETE=true
    for artifact in train.parquet validation.parquet selected_episodes.jsonl dataset_report.json; do
        if [[ ! -f ${DATASET_DIR}/${artifact} ]]; then
            echo "Existing raw dataset is incomplete; missing ${DATASET_DIR}/${artifact}" >&2
            exit 2
        fi
    done
fi

SWEEP_DATASET_COMPLETE=false
if [[ -f ${SWEEP_DATASET_ROOT}/sweep_manifest.json ]]; then
    SWEEP_DATASET_COMPLETE=true
    for arm in raw25 raw50 raw100 compact100; do
        if [[ ! -f ${SWEEP_DATASET_ROOT}/${arm}/dataset_report.json ]]; then
            echo "Existing sweep is incomplete; missing ${arm}/dataset_report.json" >&2
            exit 2
        fi
    done
elif [[ -e ${SWEEP_DATASET_ROOT} ]]; then
    for arm in raw25 raw50 raw100 compact100; do
        if [[ -e ${SWEEP_DATASET_ROOT}/${arm} ]]; then
            echo "Existing sweep has a partial arm without a manifest: ${SWEEP_DATASET_ROOT}/${arm}" >&2
            exit 2
        fi
    done
fi

cd "${PROJECT_DIR}"
export PATH=${ENV_PATH}/bin:${PATH}
export CONDA_PREFIX=${ENV_PATH}
export HF_HOME=${HF_HOME:-/zfsauton/scratch/frankwu2/.cache/huggingface}
export HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-1}
export TRANSFORMERS_OFFLINE=${TRANSFORMERS_OFFLINE:-1}
export TMPDIR=${TMPDIR:-/zfsauton/scratch/frankwu2/tmp}
export TOKENIZERS_PARALLELISM=false
mkdir -p "${HF_HOME}" "${TMPDIR}"

echo "=== Build Qwen self-RS datasets ==="
echo "input=${INPUT_JSONL}"
echo "selected_scenarios=${SELECTED_SCENARIOS} validation_fraction=${VALIDATION_FRACTION}"
echo "dataset=${DATASET_DIR} sweep=${SWEEP_DATASET_ROOT}"
echo "==================================="

if [[ ${RAW_DATASET_COMPLETE} == true ]]; then
    echo "Reusing complete raw dataset: ${DATASET_DIR}"
else
    "${PYTHON_BIN}" -m scripts.sft.build_dataset \
        --input "${INPUT_JSONL}" \
        --output-dir "${DATASET_DIR}" \
        --target-tokenizer "${TARGET_TOKENIZER}" \
        --no-target-enable-thinking \
        --target-format raw \
        --validation-fraction "${VALIDATION_FRACTION}" \
        --split-seed "${SPLIT_SEED}" \
        --selected-scenario-count "${SELECTED_SCENARIOS}" \
        --selection-seed "${SELECTION_SEED}"
fi

export DATASET_REPORT=${DATASET_DIR}/dataset_report.json
export SELF_SELECTED_EPISODES=${DATASET_DIR}/selected_episodes.jsonl
export HAIKU_SELECTED_EPISODES
export OVERLAP_REPORT=${DATASET_DIR}/haiku_scenario_overlap.json
export SELECTED_SCENARIOS VALIDATION_FRACTION
"${PYTHON_BIN}" - <<'PY'
import json
import os
from pathlib import Path

with open(os.environ["DATASET_REPORT"], encoding="utf-8") as handle:
    report = json.load(handle)
expected = int(os.environ["SELECTED_SCENARIOS"])
if report["selected_scenarios"] != expected:
    raise SystemExit(f"selected {report['selected_scenarios']} scenarios; expected {expected}")
if report["train_scenarios"] + report["validation_scenarios"] != expected:
    raise SystemExit("train/validation scenario counts do not sum to the selected target")
expected_validation = round(expected * float(os.environ["VALIDATION_FRACTION"]))
if report["validation_scenarios"] != expected_validation:
    raise SystemExit(
        f"validation split has {report['validation_scenarios']} scenarios; expected {expected_validation}"
    )
print(
    "verified raw dataset:",
    f"train={report['train_scenarios']} scenarios/{report['train_decision_rows']} turns,",
    f"validation={report['validation_scenarios']} scenarios/{report['validation_decision_rows']} turns",
)

reference_path = Path(os.environ["HAIKU_SELECTED_EPISODES"])
if reference_path.is_file():
    def load_manifest(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    self_rows = load_manifest(Path(os.environ["SELF_SELECTED_EPISODES"]))
    reference_rows = load_manifest(reference_path)
    self_ids = {str(row["scenario_id"]) for row in self_rows}
    reference_ids = {str(row["scenario_id"]) for row in reference_rows}
    overlap = self_ids & reference_ids
    overlap_report = {
        "self_selected_scenarios": len(self_ids),
        "haiku_selected_scenarios": len(reference_ids),
        "overlap_scenarios": len(overlap),
        "overlap_fraction_of_self": len(overlap) / len(self_ids) if self_ids else None,
        "haiku_manifest": str(reference_path),
        "overlap_scenario_ids": sorted(overlap),
    }
    Path(os.environ["OVERLAP_REPORT"]).write_text(
        json.dumps(overlap_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Haiku scenario overlap: {len(overlap)}/{len(self_ids)}")
else:
    print(f"Haiku manifest not found; skipping overlap report: {reference_path}")
PY

if [[ ${SWEEP_DATASET_COMPLETE} == true ]]; then
    echo "Reusing complete sweep dataset: ${SWEEP_DATASET_ROOT}"
else
    "${PYTHON_BIN}" -m scripts.sft.make_sweep_datasets \
        --source-dir "${DATASET_DIR}" \
        --output-root "${SWEEP_DATASET_ROOT}" \
        --target-tokenizer "${TARGET_TOKENIZER}" \
        --subset-seed "${SUBSET_SEED}" \
        --max-think-tokens "${MAX_THINK_TOKENS}"
fi

echo "dataset_build_complete=$(date --iso-8601=seconds)"
echo "manifest=${SWEEP_DATASET_ROOT}/sweep_manifest.json"
