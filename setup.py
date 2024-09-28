from setuptools import setup, find_packages

setup(
    name='pyverbplt',
    version='24.09',
    author='Alexander Drozdov',
    author_email='adrozdov@ucla.edu',
    description='Python library designed to load `.plt` files, created by the Versatile Electron Radiation Belts (VERB) code',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/radiation-belts/pyverbplt',
    py_modules=['pyverbplt'],  # Use py_modules for single-file modules
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
