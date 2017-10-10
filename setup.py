from setuptools import setup
import re

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('xcodetool/xcodetool.py').read(),
    re.M
    ).group(1)

setup(
  name = 'xcodetool',
  packages = ['xcodetool'],
  package_data = {
    'xcodetool': ['options/*.plist'],
  },
  entry_points = {
    "console_scripts": ['xcodetool = xcodetool.xcodetool:main']
  },
  version = version,
  description = 'A convenient python tool for xcodebuild',
  author = 'Canius Chu',
  author_email = 'canius.chu@outlook.com',
  license='MIT',
  url = 'https://github.com/canius/xcodetool',
  download_url = 'https://github.com/canius/xcodetool/archive/{}.tar.gz'.format(version),
  keywords = ['ios', 'xcode', 'build', 'xcodebuild', 'jenkins'],
  classifiers = [],
  python_requires = '>=2.7',
)