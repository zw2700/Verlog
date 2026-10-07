"""Run the actual update, output model and aggregator without the GPU stack."""
import ast
from pathlib import Path
from typing import Any, Optional

import numpy as np
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[2]


def test_completed_metrics_do_not_leak_into_next_game_or_duplicate_routed_done_rows():
    source = ast.parse((ROOT / "verl/experimental/agent_loop/agent_loop.py").read_text())
    definitions = [n for n in source.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
                   and n.name in {"AgentLoopMetrics", "AgentLoopOutput", "aggregate_env_metrics"}]
    namespace = dict(Any=Any, Optional=Optional, BaseModel=BaseModel, Field=Field, np=np)
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "actual-output-and-aggregation", "exec"), namespace)
    tree = ast.parse((ROOT / "verl/experimental/agent_loop/tool_agent_loop.py").read_text())
    run = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "run")
    loop = next(n for n in ast.walk(run) if isinstance(n, ast.While))
    start = next(i for i, n in enumerate(loop.body) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "step_env_metrics" for t in n.targets))
    update = compile(ast.Module(body=loop.body[start:start+2], type_ignores=[]), "actual-update", "exec")
    namespace['metrics'] = {}
    outputs = []
    events = [{}, {"negotiation/consensus_reached": 1, "outcome/chosen_student_rank_global": 1},
              {}, {}, {"negotiation/consensus_reached": 0, "outcome/chosen_student_rank_global": None}]
    for event in events:
        namespace['_flat_info'] = {'metrics': event}
        exec(update, namespace)
        outputs.append(namespace['AgentLoopOutput'](prompt_ids=[1], response_ids=[2], response_mask=[1],
                                                    metrics=namespace['metrics'], done=bool(event)))
    # Terminal reward routing also marks a previous professor row as done.
    outputs[0].done = True
    assert outputs[0].metrics.env_metrics == {}
    assert outputs[2].metrics.env_metrics == outputs[3].metrics.env_metrics == {}
    assert outputs[1].metrics.env_metrics == events[1]
    result = namespace['aggregate_env_metrics']([r.metrics.model_dump()['env_metrics'] for r in outputs])
    assert result['env/step/episodes_rolled_out'] == 2
    assert result['env/step/socially_optimal_rate'] == 0.5
