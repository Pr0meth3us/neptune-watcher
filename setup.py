from setuptools import setup

setup(name='neptunepy',
      version='0.1',
      description='A python wrapper for the Neptunes Pride API',
      url='http://github.com/bryantfhayes/neptunepy',
      author='Bryant Hayes',
      author_email='bryantfhayes@gmail.com',
      license='MIT',
      packages=['neptunepy', 'httpsession'],
      zip_safe=False)