from pathlib import Path

import pytest


@pytest.fixture
def testrun_zpath(testrun_uid):
    return Path(testrun_uid)
