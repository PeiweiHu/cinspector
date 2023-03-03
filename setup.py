import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install


def _gen_parser(dir_path):
    from subprocess import check_call
    check_call([sys.executable, '_gen_parser.py'],
               cwd=os.path.join(dir_path, 'cinspector'))


class CinspectorInstallCmd(install):

    def run(self):
        install.run(self)
        self.execute(_gen_parser, (self.install_lib,),
                     msg="Generate the parser")


with open('README.md') as f:
    long_description = f.read()

setup(name='cinspector',
      version='0.0.1',
      author="Peiwei Hu",
      author_email='jlu.hpw@foxmail.com',
      description='A static C source code analysis framework',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      include_package_data=True,
      url='https://github.com/PeiweiHu/cinspector',
      install_requires=[
          'tree-sitter',
          'networkx',
      ],
      tests_require=[
          'pytest',
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Operating System :: OS Independent",
      ],
      license="WTFPL",
      python_requires='>=3.6',
      cmdclass={
          'install': CinspectorInstallCmd,
      })
