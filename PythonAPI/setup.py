"""To compile and install locally run "python setup.py build_ext --inplace".
To install library to Python site-packages run "python -m pip install --use-feature=in-tree-build ."
"""
from pathlib import Path
from setuptools import setup, Extension

import numpy as np
from Cython.Build import cythonize

ext_modules = [
        Extension(
            'pycocotools._mask',
            sources=['./common/maskApi.c', 'pycocotools/_mask.pyx'],
            include_dirs=[np.get_include(), './common'],
        )
    ]

try:
    readme = Path(__file__).parent.parent.joinpath("README.md").read_text("utf-8")
except FileNotFoundError:
    readme = ""

setup(
    name='pycocotools',
    description='Official APIs for the MS-COCO dataset',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ppwwyyxx/cocoapi",
    license="FreeBSD",
    packages=['pycocotools'],
    package_dir={'pycocotools': 'pycocotools'},
    python_requires='>=3.9',
    install_requires=[
        'numpy',
    ],
    extras_require={
        'all': ['matplotlib>=2.1.0'],
    },
    version='2.0.9',
    ext_modules=cythonize(ext_modules),
)
