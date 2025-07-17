"""To compile and install locally run "python setup.py build_ext --inplace".
To install library to Python site-packages run "python -m pip install --use-feature=in-tree-build ."
"""
import platform
import sys
import sysconfig
from pathlib import Path
from setuptools import setup, Extension

import numpy as np
from Cython.Build import cythonize

py_gil_disabled = sysconfig.get_config_var('Py_GIL_DISABLED')
use_limited_api = not py_gil_disabled and platform.python_implementation() == 'CPython' and sys.version_info >= (3, 12)
if use_limited_api:
    limited_api_args = {
        "py_limited_api": True,
        "define_macros": [("Py_LIMITED_API", "0x030C0000")],
    }
    options = {"bdist_wheel": {"py_limited_api": "cp312"}}
else:
    limited_api_args = {}
    options = {}

ext_modules = [
        Extension(
            'pycocotools._mask',
            sources=['./common/maskApi.c', 'pycocotools/_mask.pyx'],
            include_dirs=[np.get_include(), './common'],
            **limited_api_args
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
    version='2.0.10',
    ext_modules=cythonize(ext_modules),
    options=options,
)
