import sys

try:
    from oguilem.ui.general import OGUILEMApplication
except ModuleNotFoundError:
    print("Please install this module (pip install) before using! Alternatively, add to PYTHONPATH.")
    sys.exit(1)

app = OGUILEMApplication(sys.argv)
sys.exit(app.run())
