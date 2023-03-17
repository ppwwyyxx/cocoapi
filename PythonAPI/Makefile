all:
    # install pycocotools locally
	python3 setup.py build_ext --inplace
	rm -rf build

install:
	# install pycocotools to the Python site-packages
	python3 -m pip install --use-feature=in-tree-build .
	rm -rf build