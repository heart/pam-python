#!/bin/bash

rm -rd dist
rm -rf pam_python.egg-info

pip install build twine
python -m build
python -m twine upload dist/*