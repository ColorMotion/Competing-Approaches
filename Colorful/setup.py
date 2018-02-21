from setuptools import setup
import sys

try:
    import caffe
except ImportError:
    print('caffe must be installed separately as a system site package', file=sys.stderr)
    raise SystemExit(1)


setup(
    name='colorful-dependencies',
    version='0.0.1',
    description="Dummy package with Colorful's dependencies.",
    install_requires=['scikit-image'],
)
