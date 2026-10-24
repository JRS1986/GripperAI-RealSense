"""
Setup of meshpy python codebase
Author: Jeff Mahler
"""
from setuptools import setup

requirements = [
    'numpy>=1.26',
    'scipy>=1.11',
    'autolab_core>=1.1',
    'matplotlib>=3.8',
    'opencv-python>=4.10',
    'Pillow>=10.3',
    'pypng',
    'scikit-image>=0.22',
    'scikit-learn>=1.5',
]

exec(open('perception/version.py').read())

setup(name='autolab_perception',
      version=__version__,
      description='Perception utilities for the Berkeley AutoLab',
      author='Jeff Mahler',
      author_email='jmahler@berkeley.edu',
      license = 'Apache Software License',
      url = 'https://github.com/BerkeleyAutomation/perception',
      keywords = 'robotics grasping vision perception',
      classifiers = [
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Natural Language :: English',
          'Topic :: Scientific/Engineering'
      ],
      packages=['perception'],
      install_requires = requirements,
      python_requires = '>=3.10',
      extras_require = { 'video' : ['scikit-video'],
                         'serial' : ['pyserial>=3.4'],
                         'docs' : [
                            'sphinx',
                            'sphinxcontrib-napoleon',
                            'sphinx_rtd_theme'
                        ],
                       'ros' : [
                           'primesense',
                           'rospkg',
                           'catkin_pkg',
                           'empy'
                        ],
    }
)
