from setuptools import setup, find_packages
import mdbg

setup(name='Markdown BG',
      version=mdbg.__version__,
      description='Markdown BG is an improvement of the existing Mardown language.',
      long_description=open('README.md').read(),
      url='https://yopox.github.io/mdbg/',
      author='yopox',
      author_email="yopoxdev@gmail.com",
      license='MPL-2.0',
      include_package_data=True,
      packages=find_packages(),
      install_requires= open('requirements.txt').read().split('\n'),
      classifier=[
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
      ],
      entry_points = {
        'gui_scripts': [
            'mdbg = mdbg.main:main',
        ],
    },
)
