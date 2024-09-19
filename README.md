# pyverbplt

**pyverbplt** is a Python library designed to load `.plt` files, created by the Versatile Electron Radiation Belts (VERB) code into structured numpy arrays. 

## Features

- Load data from `.plt` files into structured numpy arrays.
- Supports loading multiple variables from the `.plt` file.
- Options to permute, squeeze, and reshape the loaded data.
- Ability to specify zones for selective data loading.

## Installation

To install pyverbplt, clone the repository:
```bash
git clone https://github.com/radiation-belts/pyverbplt.git
```

To install using PyPI:
```bash
pip install pyverbplt
```


## Usage
The main functionality is provided by the `load_plt` function in `pyverbplt.py`. Below are some examples of how to use this function:

```python
import pyverbplt

# Example 1: Load multiple variables from a diffusion coefficients .plt file
L, E, A, Daa = pyverbplt.load_plt('path/to/dxx_file.plt')

# Example 2: Load data from a .plt file but only unpack one variable
_, _, _, Daa = pyverbplt.load_plt('path/to/dxx_file.plt')

# Example 3: Load data from a PSD .plt file into a single variable. Load all zones (times).
psd = pyverbplt.load_plt('path/to/psd_file.plt', first_zone=0, skip_zones=0, n_zones=None)
```

## Documentation
Please see the file header. The readthedoc version is comming soon.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
