from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='cinspector',
    version='0.0.1',
    author="Peiwei Hu",
    author_email='jlu.hpw@foxmail.com',
    description='A static C source code analysis framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={'': ['*.so']},
    include_package_data=True,
    url='https://github.com/PeiweiHu/cinspector',
    install_requires=[
        'tree-sitter',
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
)
