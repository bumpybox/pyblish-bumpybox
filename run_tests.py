import os

import pytest


pytest.main(
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "tests"))]
)
