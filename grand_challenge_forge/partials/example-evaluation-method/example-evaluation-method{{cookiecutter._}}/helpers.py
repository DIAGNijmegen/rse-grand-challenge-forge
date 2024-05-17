import multiprocessing
import os
import signal
from concurrent.futures import as_completed
from multiprocessing import Manager, Process

import psutil
from pebble import ProcessPool


class PredictionProcessingError(RuntimeError):
    def __init__(self, prediction):
        self.prediction = prediction

    def __str__(self):
        return f"Error for prediction: {self.prediction}"


def get_max_workers():
    """
    Returns the maximum number of concurrent workers

    The optimal number of workers ultimately depends on how many resources
    each process will call upon.

    To limit this, update the Dockerfile GRAND_CHALLENGE_MAX_WORKERS
    """

    environ_cpu_limit = os.getenv("GRAND_CHALLENGE_MAX_WORKERS")
    cpu_count = multiprocessing.cpu_count()
    return min(
        [
            int(environ_cpu_limit or cpu_count),
            cpu_count,
        ]
    )


def run_prediction_processing(*, fn, predictions):
    """
    Processes predictions in separate processes.

    This takes child processes into account:
    - if any child process is terminated, all prediction processing will abort
    - after prediction processing is done, all child processes are terminated

    Parameters
    ----------
    fn : function
        Function to execute.

    predictions : list
        List of predictions.

    """
    with Manager() as manager:
        results = manager.list()
        errors = manager.list()

        process = Process(
            target=__pool_worker,
            name="PredictionProcessing",
            kwargs=dict(
                fn=fn,
                predictions=predictions,
                max_workers=get_max_workers(),
                results=results,
                errors=errors,
            ),
        )
        try:
            process.start()
            process.join()
        finally:
            process.close()

        for prediction, e in errors:
            raise PredictionProcessingError(prediction=prediction) from e

        return list(results)


def __pool_worker(*, fn, predictions, max_workers, results, errors):
    terminating_child_processes = False
    with ProcessPool(max_workers=max_workers) as pool:
        try:

            def sigchld_handler(*_, **__):
                if not terminating_child_processes:
                    pool.stop()
                    raise RuntimeError(
                        "Child process was terminated unexpectedly"
                    )

            # Register the SIGCHLD handler
            signal.signal(signal.SIGCHLD, sigchld_handler)

            # Submit the processing tasks of the predictions
            futures = [
                pool.schedule(fn, [prediction]) for prediction in predictions
            ]
            future_to_predictions = {
                future: item
                for future, item in zip(futures, predictions, strict=True)
            }

            for future in as_completed(future_to_predictions):
                try:
                    result = future.result()
                except Exception as e:
                    for f in futures:
                        f.cancel()
                    pool.stop()
                    errors.append((future_to_predictions[future], e))
                results.append(result)
        finally:
            terminating_child_processes = True
            terminate_child_processes()


def terminate_child_processes():
    current_process = psutil.Process(os.getpid())
    children = current_process.children(recursive=True)
    for child in children:
        child.terminate()

    # Wait for processes to terminate
    gone, still_alive = psutil.wait_procs(children, timeout=5)

    # Forcefully kill any remaining processes
    for p in still_alive:
        print(f"Forcefully killing child process {p.pid}")
        p.kill()
