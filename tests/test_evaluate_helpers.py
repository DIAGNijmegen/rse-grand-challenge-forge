import os
import sys
import time
from functools import partial
from multiprocessing import Process
from unittest import mock

import psutil
import pytest

# Do some creating path hacking to be able to import the helpers
parent_dir = os.path.abspath(
    os.path.join(
        "grand_challenge_forge",
        "partials",
        "example-evaluation-method",
    )
)
sys.path.insert(0, parent_dir)

from helpers import (  # noqa: E402
    PredictionProcessingError,
    _start_pool_worker,
    run_prediction_processing,
)

# Some of the test below, if things go wrong, can potentially deadlock.
# So we set a maximum runtime
pytestmark = pytest.mark.timeout(4)


def working_process(p):
    if p["pk"] == "prediction1":
        time.sleep(2)
    return f"{p['pk']} result"


def failing_process(*_):
    raise RuntimeError("You have failed me for the last time")


def child_process():
    while True:
        print("Child busy")
        time.sleep(1)


def child_spawning_process(*_):
    child = Process(target=child_process)
    child.start()
    return "Done"


def forever_process(*_):
    while True:
        time.sleep(1)


def stop_children(process, interval):
    stopped = False
    while not stopped:
        process = psutil.Process(process.pid)
        children = process.children(recursive=True)
        if children:
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass  # Not a problem
            stopped = True
        time.sleep(interval)


def test_prediction_processing():
    predictions = [{"pk": "prediction1"}, {"pk": "prediction2"}]
    result = run_prediction_processing(
        fn=working_process, predictions=predictions
    )
    assert {"prediction1 result", "prediction2 result"} == set(result)


def test_prediction_processing_error():
    predictions = [
        {"pk": "prediction1"}
    ]  # Use one prediction for reproducibility
    with pytest.raises(PredictionProcessingError):
        run_prediction_processing(fn=failing_process, predictions=predictions)


def test_prediction_processing_killing_of_child_processes():
    # If something goes wrong, this test could deadlock
    # 5 seconds should be more than enough

    predictions = [{"pk": "prediction1"}, {"pk": "prediction2"}]
    result = run_prediction_processing(
        fn=child_spawning_process, predictions=predictions
    )

    # The above call returning already shows that it correctly terminates
    # child processes, just for sanity:
    assert len(result) == len(predictions)


def test_prediction_processing_catching_killing_of_child_processes():
    predictions = [{"pk": "prediction1"}, {"pk": "prediction2"}]

    child_stopper = None

    # Set up the fake child murder scene
    def add_child_terminator(*args, **kwargs):
        process = _start_pool_worker(*args, **kwargs)
        nonlocal child_stopper
        child_stopper = Process(target=partial(stop_children, process, 0.5))
        child_stopper.start()  # Hasta la vista, baby
        return process

    try:
        with mock.patch("helpers._start_pool_worker", add_child_terminator):
            with pytest.raises(PredictionProcessingError):
                run_prediction_processing(
                    fn=forever_process, predictions=predictions
                )
    finally:
        if child_stopper:
            child_stopper.terminate()
