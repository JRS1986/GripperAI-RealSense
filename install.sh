# small install script for this GripperViewContainer. Will probably not work all the time

# needed: python(2) and python3, with pip and pip3
pip install -r requirements.txt
pip3 install -r requirements.txt
pip install perception_exactly_this_is_somehow_required/
#irgendwie installiert der bei mir numpy immer doppelt...
pip uninstall numpy 
cd gqcnn_jeffbranch_adapted && python setup.py install && cd ..

#viel erfolg
