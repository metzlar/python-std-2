from setuptools import setup, find_packages

setup(
  name='Python Utilities',
  version='0.1',
  packages=find_packages(),
  cmdclass={'upload':lambda x:None},
  install_requires=[
  ],
)# pragma: no cover  
