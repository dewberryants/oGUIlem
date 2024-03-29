from setuptools import setup, find_packages

with open('./README.md') as f:
    readme = f.read()

with open('./LICENSE') as f:
    lic = f.read()

packages = find_packages()

setup(
    name='OGUILEM',
    version='0.0.5',
    description='A GUI for OGOLEM',
    long_description=readme,
    author='Dominik Behrens',
    author_email='dewberryants@gmail.com',
    url='https://github.com/dewberryants/oGUIlem',
    license=lic,
    packages=packages,
    install_requires=['matplotlib' , 'numpy'],
    package_data={'': ['*.xml', '*.ico', '*.ogo']}
)
