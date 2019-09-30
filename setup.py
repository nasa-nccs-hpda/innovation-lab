import sys, os
from setuptools import setup, find_packages

setup(name='mmx',
      version='1.0',
      description='MMX module for PC2',
      author='Innovation Lab',
      author_email='thomas.maxwell@nasa.gov',
      url='https://github.com/nasa-nccs-hpda/innovation-lab/tree/mmx_alone',
      packages=find_packages(),
      package_data={ 'mmx.data': ['csv/*.csv',"merra/*.nc"], 'mmx.model': [ 'libraries/*.jar' ] },
      zip_safe=False )





