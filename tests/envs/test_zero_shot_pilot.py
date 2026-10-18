"""CPU integration checks for the exact runner and canonical Slurm dispatch."""

import json
import os
import re
import subprocess
import sys
import types
from itertools import permutations
from pathlib import Path

import pytest
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]
for name, path in [
    ("verl", ROOT / "verl"),
    ("verl.envs", ROOT / "verl/envs"),
    ("verl.envs.hiring_env", ROOT / "verl/envs/hiring_env"),
]:
    package = sys.modules.setdefault(name, types.ModuleType(name))
    package.__path__ = [str(path)]

from scripts import rollout_frontier as frontier  # noqa: E402
from scripts import zero_shot_pilot as pilot  # noqa: E402


def config_for(tmp_path, **overrides):
    with initialize_config_dir(config_dir=str(ROOT / "configs"), version_base=None):
        config = compose(config_name="zero_shot_pilot")
    config = OmegaConf.to_container(config, resolve=True)
    config.update(
        backend="fake", num_episodes=3, batch_size=4, output_dir=str(tmp_path / "run"), require_clean_git=False
    )
    config.update(overrides)
    return config


def test_batched_pilot_pairs_scenarios_and_writes_auditable_artifacts(tmp_path):
    config = config_for(tmp_path)
    summary = pilot.run_pilot(config)
    output = Path(config["output_dir"])
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["fake_results"] is True
    assert manifest["completed_episodes"] == 9
    assert manifest["paired_scenarios_verified"] == 3
    rows = [json.loads(line) for line in (output / "results.jsonl").read_text().splitlines()]
    for seed in range(3):
        paired = [row for row in rows if row["seed"] == seed]
        assert len(paired) == 3
        assert len({row["scenario_sha256"] for row in paired}) == 1
    for condition in config["conditions"]:
        assert summary[condition]["episodes"] == 3
        assert summary[condition]["agreement_rate"] == 1
        assert summary[condition]["invalid_actions"] == 0
        shard = output / condition / "episodes/episodes.worker00.jsonl"
        episodes = [json.loads(line) for line in shard.read_text().splitlines()]
        assert len(episodes) == 3
        assert all(episode["rollout_metadata"]["scenario_seed"] in range(3) for episode in episodes)
        expected_calls = 2 if condition == "baseline" else 9
        assert all(len(episode["turns"]) == expected_calls for episode in episodes)
        if condition != "baseline":
            assert {turn["phase"] for turn in episodes[0]["turns"]} == {"discussion", "readiness", "ballot"}


def test_actual_model_inputs_keep_thoughts_private_and_withhold_control_messages(tmp_path):
    class SpyClient:
        tokenizer = None

        def complete_batch(self, messages, seeds):
            results = []
            for observation in messages:
                text = "\n".join(message["content"] for message in observation)
                actor = re.search(r"You are Professor (prof_\d+)", text)[1]
                others = set(("prof_1", "prof_2", "prof_3")) - {actor}
                for other in others:
                    assert f"SECRET_THOUGHT_{other}" not in text
                    if "PUBLIC COMMUNICATION IS DISABLED" in text:
                        assert f"SPEECH_{other}" not in observation[-1]["content"]
                if "PHASE: discussion;" in text:
                    action = f"<GROUP>SPEECH_{actor}</GROUP>"
                elif "PHASE: readiness;" in text:
                    action = "<READY_TO_VOTE>"
                else:
                    action = "<VOTE>0</VOTE>"
                results.append(frontier.Completion(text=f"<THINK>SECRET_THOUGHT_{actor}</THINK>{action}"))
            return results

    config = config_for(tmp_path)
    summary = pilot.run_pilot(config, client=SpyClient())
    assert summary["deliberation"]["mean_public_messages"] == 3
    assert summary["deliberation_no_communication"]["mean_public_messages"] == 0
    normal = json.loads(
        (Path(config["output_dir"]) / "deliberation/episodes/episodes.worker00.jsonl").read_text().splitlines()[0]
    )
    control = json.loads(
        (Path(config["output_dir"]) / "deliberation_no_communication/episodes/episodes.worker00.jsonl")
        .read_text()
        .splitlines()[0]
    )
    assert normal["tokens_used"] == control["tokens_used"] == 3
    assert control["flat_metrics"]["deliberation/withheld_messages"] == 3


def test_dry_run_creates_no_output_or_model(tmp_path):
    config = config_for(tmp_path, backend="vllm", dry_run=True)
    plan = pilot.run_pilot(config)
    assert plan["status"] == "planned"
    assert not Path(config["output_dir"]).exists()


def test_existing_results_are_never_overwritten(tmp_path):
    config = config_for(tmp_path)
    output = Path(config["output_dir"])
    output.mkdir()
    (output / "evidence.txt").write_text("keep")
    with pytest.raises(FileExistsError):
        pilot.run_pilot(config)
    assert (output / "evidence.txt").read_text() == "keep"


def test_incomplete_client_batch_fails_loudly_and_records_failure(tmp_path):
    class BrokenClient:
        tokenizer = None

        def complete_batch(self, messages, seeds):
            return []

    config = config_for(tmp_path)
    with pytest.raises(ValueError, match="completion count"):
        pilot.run_pilot(config, client=BrokenClient())
    manifest = json.loads((Path(config["output_dir"]) / "manifest.json").read_text())
    assert manifest["status"] == "failed"


def test_gpu_execution_refuses_dirty_source_before_model_load(tmp_path, monkeypatch):
    config = config_for(tmp_path, backend="vllm", require_clean_git=True)
    monkeypatch.setattr(pilot, "source_provenance", lambda: {"dirty": True})
    with pytest.raises(ValueError, match="clean commit-pinned checkout"):
        pilot.run_pilot(config)
    assert not Path(config["output_dir"]).exists()


def test_real_model_cannot_start_on_an_unallocated_login_node(tmp_path, monkeypatch):
    config = config_for(tmp_path, backend="vllm", require_clean_git=True)
    monkeypatch.setattr(pilot, "source_provenance", lambda: {"dirty": False})
    monkeypatch.delenv("SLURM_JOB_ID", raising=False)
    with pytest.raises(ValueError, match="Slurm GPU allocation"):
        pilot.run_pilot(config)
    assert not Path(config["output_dir"]).exists()


def test_batch_width_does_not_change_scenarios_or_fake_results(tmp_path):
    configs = [config_for(tmp_path, batch_size=width, output_dir=str(tmp_path / str(width))) for width in (1, 7)]
    records = []
    for config in configs:
        pilot.run_pilot(config)
        rows = [json.loads(line) for line in (Path(config["output_dir"]) / "results.jsonl").read_text().splitlines()]
        records.append(
            {
                (row["condition"], row["seed"]): (
                    row["scenario_sha256"],
                    row["consensus"],
                    row["social_welfare_efficiency"],
                    row["turns"],
                )
                for row in rows
            }
        )
    assert records[0] == records[1]


def test_sampling_seeds_do_not_depend_on_ballot_submission_order():
    expected = None
    for order in permutations(("prof_1", "prof_2", "prof_3")):
        seeds = {
            actor: pilot.request_seed(2026, 7, {"agent_id": actor, "phase": "ballot", "actor_phase_turn": 1})
            for actor in order
        }
        if expected is None:
            expected = seeds
        assert seeds == expected


def test_real_hydra_cli_dry_run_has_no_file_side_effects(tmp_path):
    bootstrap = (
        "import runpy, sys, types\n"
        f"from pathlib import Path\nroot=Path({str(ROOT)!r})\n"
        "for name, path in [('verl',root/'verl'),('verl.envs',root/'verl/envs'),"
        "('verl.envs.hiring_env',root/'verl/envs/hiring_env')]:\n"
        "    package=types.ModuleType(name); package.__path__=[str(path)]; sys.modules[name]=package\n"
        "runpy.run_module('scripts.zero_shot_pilot',run_name='__main__')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    result = subprocess.run(
        [sys.executable, "-c", bootstrap, "dry_run=true"],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout)["status"] == "planned"
    assert list(tmp_path.iterdir()) == []


def test_local_vllm_adapter_uses_batched_chat_request_seeds_and_real_token_counts(tmp_path, monkeypatch):
    calls = {}

    class Sampling:
        def __init__(self, **kwargs):
            self.values = kwargs

    class Model:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def get_tokenizer(self):
            return "tokenizer"

        def chat(self, messages, **kwargs):
            calls["chat"] = kwargs
            return [
                types.SimpleNamespace(
                    prompt_token_ids=[1, 2], outputs=[types.SimpleNamespace(text="answer", token_ids=[3, 4, 5])]
                )
                for _ in messages
            ]

    monkeypatch.setitem(sys.modules, "vllm", types.SimpleNamespace(LLM=Model, SamplingParams=Sampling))
    client = pilot.LocalVLLMClient(config_for(tmp_path))
    results = client.complete_batch([[{"role": "user", "content": "x"}]] * 2, [11, 22])
    assert [params.values["seed"] for params in calls["chat"]["sampling_params"]] == [11, 22]
    assert calls["chat"]["chat_template_kwargs"] == {"enable_thinking": False}
    assert results[0].prompt_tokens == 2
    assert results[0].response_tokens == 3
    assert client.tokenizer == "tokenizer"


@pytest.mark.parametrize("protocol", ["async_ticker", "deliberation_voting"])
def test_existing_frontier_runner_uses_real_factory_and_phase_aware_fake_client(tmp_path, protocol):
    config = {**frontier.DEFAULT_ENV_CONFIG, "protocol": protocol}
    result = frontier.run_episode(
        client=frontier.FakeVoteClient(),
        env_config=config,
        seed=8,
        env_idx=0,
        episode_index=0,
        epoch=-1,
        global_steps=0,
        out_jsonl=tmp_path / "episodes.jsonl",
        game_log=None,
        provider_name="fake",
        model_name="fake",
        include_raw_response=False,
    )
    assert result["consensus"]
    assert result["turns"] == (2 if protocol == "async_ticker" else 9)


@pytest.mark.parametrize("mode,module", [("train", "verl.trainer.main_ppo"), ("zero_shot", "scripts.zero_shot_pilot")])
def test_canonical_slurm_entrypoint_dispatches_without_loading_a_gpu(tmp_path, mode, module):
    (tmp_path / "slurm").mkdir()
    (tmp_path / "slurm/common.sh").write_text('PYTHON_BIN="$PROJECT_DIR/python-stub"\n')
    stub = tmp_path / "python-stub"
    stub.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > "$PROJECT_DIR/arguments.txt"\n')
    stub.chmod(0o700)
    env = {
        **os.environ,
        "PROJECT_DIR": str(tmp_path),
        "VERLOG_JOB_MODE": mode,
        "SLURM_CPUS_PER_TASK": "8",
        "JOB_ID": "test",
    }
    subprocess.run(
        ["bash", str(ROOT / "slurm/train_auton.sbatch"), "tag=test"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    arguments = (tmp_path / "arguments.txt").read_text().splitlines()
    assert arguments[:2] == ["-m", module]
    assert arguments[-1] == "tag=test"


@pytest.mark.parametrize("layout", ["remapped", "shared"])
@pytest.mark.parametrize("gpu_state", ["free", "busy", "query_failed"])
def test_shared_setup_resolves_remapped_gpus_and_preserves_occupancy_guard(tmp_path, layout, gpu_state):
    (tmp_path / "bin").mkdir()
    nvidia = tmp_path / "bin/nvidia-smi"
    allocated = "GPU-00000000-0000-0000-0000-000000000005"
    nvidia.write_text(
        '#!/bin/bash\nprintf "%s\\n" "$*" >> "$GPU_TEST_LOG"\n'
        f'allocated="{allocated}"\n'
        'case "$*" in\n'
        '  --query-gpu=uuid*)\n'
        '    [ "$GPU_TEST_LAYOUT" != shared ] || echo GPU-00000000-0000-0000-0000-000000000000\n'
        '    echo "$allocated" ;;\n'
        '  "-i 5 --query-gpu=uuid"*)\n'
        '    if [ "$GPU_TEST_LAYOUT" = shared ]; then echo "$allocated";\n'
        '    else echo "No devices were found"; exit 6; fi ;;\n'
        '  "-i $allocated --query-gpu=pci.bus_id"*) echo 00000000:81:00.0 ;;\n'
        '  "-i $allocated --query-compute-apps="*)\n'
        '    case "$GPU_TEST_STATE" in\n'
        '      busy) echo "$allocated, 1234, 8000" ;;\n'
        '      query_failed) echo "No devices were found"; exit 6 ;;\n'
        '    esac ;;\n'
        '  *--query-compute-apps=*) echo "An unallocated GPU has a process" ;;\n'
        'esac\n'
    )
    nvidia.chmod(0o700)
    env = {
        **os.environ,
        "PATH": f"{tmp_path}/bin:{os.environ['PATH']}",
        "PROJECT_DIR": str(tmp_path),
        "ENV_PATH": str(tmp_path),
        "VERLOG_JOB_MODE": "zero_shot",
        "CUDA_VISIBLE_DEVICES": "0",
        "SLURM_JOB_GPUS": "5",
        "SLURM_JOB_ID": "test",
        "SLURM_TMPDIR": str(tmp_path / "tmp"),
        "GPU_TEST_LOG": str(tmp_path / "gpu-calls.log"),
        "GPU_TEST_LAYOUT": layout,
        "GPU_TEST_STATE": gpu_state,
    }
    env.pop("DATA_DIR", None)
    env.pop("VLLM_WORKER_MULTIPROC_METHOD", None)
    result = subprocess.run(
        [
            "bash",
            "-c",
            f'source "{ROOT}/slurm/common.sh"; echo "CUDA_STILL=$CUDA_VISIBLE_DEVICES"; '
            'echo "VLLM_METHOD=$VLLM_WORKER_MULTIPROC_METHOD"',
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    queries = (tmp_path / "gpu-calls.log").read_text().splitlines()
    compute_query = next(query for query in queries if "--query-compute-apps" in query)
    assert compute_query.startswith(f"-i {allocated} ")
    if gpu_state == "free":
        assert result.returncode == 0, result.stderr
        assert "CUDA_STILL=0" in result.stdout
        assert "VLLM_METHOD=spawn" in result.stdout
    else:
        assert result.returncode == 42
        expected = "already contain compute processes" if gpu_state == "busy" else "cannot query compute processes"
        assert expected in result.stderr
