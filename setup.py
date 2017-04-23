from setuptools import setup

setup(name='neptunepy',
      version='0.1',
      description='A python wrapper for the Neptunes Pride API',
      url='http://github.com/bryantfhayes/neptunepy',
      author='Bryant Hayes',
      author_email='bryantfhayes@gmail.com',
      license='MIT',
      packages=['neptunepy'],
      dependency_links=['https://github.com/bryantfhayes/bhutils/zipball/master#egg=bhutils-1.0.1'],
      install_requires=['bhutils', 'mpldatacursor', 'PyQt4'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)