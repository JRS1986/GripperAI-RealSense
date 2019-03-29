# small install script for this GripperViewContainer. Will probably not work 100% all the time, have fun debugging!

# needed: python(2) and python3, with pip and pip3
pip install -r requirements.txt
pip3 install -r requirements.txt
cd gqcnn_jeffbranch_adapted && python setup.py install && cd ..
