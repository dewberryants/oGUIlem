# OGUILEM

A graphical user interface (GUI) for the global optimization program paket [OGOLEM](https://www.ogolem.org/).

Because OGOLEM is very prohibitive in its initial setup of calculations, this simple GUI aims to simplify the process by
providing guidance and additional documentation.

## Features

* Save and Load OGOLEM configuration files (*.ogo)
* Modify and construct geometry, local as well as global optimization algorithms with easy building blocks
* (Coming soon) Easily read and visualize OGOLEM output as the optimization is running

## Installation

Requires:

* git
* python
* python-PyQT5

To install, start by cloning the GIT repo:
> git clone https://github.com/dewberryants/oGUIlem.git

Change into the repo directory and:
> pip install --user .

To run the program:
> python -m oguilem
