import os
import sys
import pytest

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    os.chdir(project_root)
    sys.exit(pytest.main(sys.argv[1:]))
