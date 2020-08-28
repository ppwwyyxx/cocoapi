"""To compile and install locally run "python setup.py build_ext --inplace".
To install library to Python site-packages run "python setup.py build_ext install"
"""
import platform
from setuptools import dist, setup, Extension

setup_requires = [
    'setuptools>=18.0',
    'cython>=0.27.3',
    'numpy',
]
dist.Distribution().fetch_build_eggs(setup_requires)

import numpy as np

ext_modules = [
        Extension(
            'pycocotools._mask',
            sources=['./common/maskApi.c', 'pycocotools/_mask.pyx'],
            include_dirs=[np.get_include(), './common'],
            extra_compile_args=[] if platform.system()=='Windows' else
            ['-Wno-cpp', '-Wno-unused-function', '-std=c99'],
        )
    ]

setup(
    name='pycocotools',
    description='Official APIs for the MS-COCO dataset',
    packages=['pycocotools'],
    package_dir={'pycocotools': 'pycocotools'},
    setup_requires=setup_requires,
    install_requires=[
        'setuptools>=18.0',
        'cython>=0.27.3',
        'matplotlib>=2.1.0'
    ],
    version='2.0.2',
    ext_modules=ext_modules
)
