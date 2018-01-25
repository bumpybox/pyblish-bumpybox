import os
import sys

import pytest


sys.exit(pytest.main(
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "tests"))]
))
