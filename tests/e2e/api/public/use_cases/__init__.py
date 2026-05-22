import os
import sys


package_dir = os.path.abspath(os.curdir)
namespace_dir = f"{package_dir}{os.path.sep}src{os.path.sep}"

sys.path.insert(0, namespace_dir)
