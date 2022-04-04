import sys

try:
    from oguilem.ui.general import OGUILEMApplication
    from oguilem.configuration import conf
except ModuleNotFoundError:
    print("Please install this module (pip install) before using! Alternatively, add to PYTHONPATH. If you have already"
          " done so, this might be caused by a missing Matplotlib or Numpy Requirement!")
    sys.exit(1)

app = OGUILEMApplication(sys.argv)
exit_code = app.run()
conf.ui.save_to_file()
sys.exit(exit_code)
