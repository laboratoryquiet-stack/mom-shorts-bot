import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests import stub_deps as _stub_deps
_stub_deps.install()
