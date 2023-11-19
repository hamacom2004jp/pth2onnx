from torch2onnx import version
from setuptools import setup


DESCRIPTION = 'torch2onnx: Convert PyTorch model to Onnx model.'
NAME = 'torch2onnx'
AUTHOR = 'hamacom2004jp'
AUTHOR_EMAIL = 'hamacom2004jp@gmail.com'
URL = 'https://github.com/hamacom2004jp/torch2onnx'
LICENSE = 'MIT'
DOWNLOAD_URL = URL
VERSION = version.__version__
PYTHON_REQUIRES = '>=3.8'
INSTALL_REQUIRES = [
    'numpy',
    'opencv-python',
    'Pillow',
    'PyYAML',
    'requests',
    'tabulate',
    'twine',
    'wheel'
]
PACKAGES = [
    'torch2onnx',
    'torch2onnx.app',
    'torch2onnx.app.convert'
]
KEYWORDS = 'pytorch onnx convert image ai model'
CLASSIFIERS=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: Japanese',
    'Programming Language :: Python',
    'Topic :: Utilities'
]
with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()
LONG_DESCRIPTION = readme
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
RESORCE_TEXT_FILES = dict(vp4onnx=[
    'config.yml', 'logconf.yml', 'scripts/torch2onnx.bat', 'scripts/torch2onnx'])

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    url=URL,
    download_url=URL,
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    license=LICENSE,
    keywords=KEYWORDS,
    install_requires=INSTALL_REQUIRES,
    package_data=RESORCE_TEXT_FILES,
    include_package_data=True,
    scripts=['torch2onnx/scripts/torch2onnx.bat','torch2onnx/scripts/torch2onnx']
)