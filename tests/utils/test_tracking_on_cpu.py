import pytest

from verl.utils.tracking import Tracking


class _Backend:
    def __init__(self, *, error=None):
        self.calls = []
        self.error = error

    def finish(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error


def _tracking_with_backends(**backends):
    tracking = Tracking.__new__(Tracking)
    tracking.logger = backends
    tracking._finished = False
    return tracking


def test_finish_is_idempotent_and_propagates_exit_code_to_wandb():
    wandb = _Backend()
    file_logger = _Backend()
    tracking = _tracking_with_backends(wandb=wandb, file=file_logger)

    tracking.finish(exit_code=1)
    tracking.finish(exit_code=0)

    assert wandb.calls == [{"exit_code": 1}]
    assert file_logger.calls == [{}]


def test_finish_attempts_remaining_backends_after_one_fails():
    wandb = _Backend(error=RuntimeError("transport closed"))
    file_logger = _Backend()
    tracking = _tracking_with_backends(wandb=wandb, file=file_logger)

    with pytest.warns(RuntimeWarning, match="Failed to finish wandb tracking cleanly"):
        tracking.finish(exit_code=0)

    assert wandb.calls == [{"exit_code": 0}]
    assert file_logger.calls == [{}]
