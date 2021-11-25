
# pycocotools

This is the source of the pypi package pycocotools, available for download at [pypi](https://pypi.org/project/pycocotools/).
It is a fork of the original [cocoapi](https://github.com/cocodataset/cocoapi), with some small fixes and packaging improvements:

* Add CircleCI tests
* Correct dependencies so it's pip-installable
* Support windows
* Don't import matplotlib unless needed
* Close file handle after openning
* Fix a small bug in rleToBbox
