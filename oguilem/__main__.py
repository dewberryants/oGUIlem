import sys

try:
    from oguilem.ui.general import OGUILEMApplication
    from oguilem.configuration import conf
except ModuleNotFoundError:
    print("Please install this module (pip install) before using! Alternatively, add to PYTHONPATH.")
    sys.exit(1)

app = OGUILEMApplication(sys.argv)
exit_code = app.run()
conf.ui.save_to_file()
sys.exit(exit_code)
