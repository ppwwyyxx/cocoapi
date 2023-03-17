"""To compile and install locally run "python setup.py build_ext --inplace".
To install library to Python site-packages run "python -m pip install --use-feature=in-tree-build ."
"""
import platform
from setuptools import setup, Extension

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
    url="https://github.com/ppwwyyxx/cocoapi",
    license="FreeBSD",
    packages=['pycocotools'],
    package_dir={'pycocotools': 'pycocotools'},
    python_requires='>=3.5',
    install_requires=[
        'matplotlib>=2.1.0',
        'numpy',
    ],
    version='2.0.6',
    ext_modules=ext_modules
)
