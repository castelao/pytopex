from setuptools import setup, find_packages

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: MIT License 
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.1'

setup(name = 'topex',
      version = version,
      description = "A very simple library to interpret and load TOPEX/JASON altimetry data",
      long_description = """\
A very simple library to read the NetCDF altimetry data of TOPEX and JASON-1. The objective here is automatize the procedure to make that dataset ready to use. This include read how many NetCDF files as required, sub-sample by time/period desired and create an accumulated intuitively dictionary of the pertinent data.

It's not implemented yet but the most interesting feature would be the class TOPEX, which would made very simple and intuitive load, sub-sample and deal with those dataset""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='altimetry, TOPEX, JASON-1, oceanography, Sea Surface Height',
      author = 'Guilherme Castelao',
      author_email = 'guilherme@castelao.net',
      url = 'http://cheeseshop.python.org/pypi/TOPEX',
      download_url = 'http://cheeseshop.python.org/packages/source/t/topex/topex-0.1.tar.gz',
      license = 'MIT',
      platforms = ['any'],
      py_modules=['topex'],
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
     )



