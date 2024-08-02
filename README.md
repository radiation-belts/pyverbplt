# pyverbplt

*pyverbplt* is a Python library designed to load `.plt` files, created by the Versetile Electron Radiaion Belts (VERB) code into structured numpy arrays. 
It provides flexible options for handling the data, including permutations, squeezing, and reshaping. 

## Features

- Load data from `.plt` files into structured numpy arrays.
- Options to permute, squeeze, and reshape the loaded data.
- Supports loading multiple variables from the `.plt` file.
- Ability to specify zones for selective data loading.

## Installation

To install pyverbplt, clone the repository:
```bash
git clone https://github.com/yourusername/pyverbplt.git
```
The PyPI package is comming soon.

## Usage
The main functionality is provided by the `load_plt` function in `pyverbplt.py`. Below are some examples of how to use this function:

```python
import pyverbplt

# Example 1: Load multiple variables from a .plt file and unpack them into separate variables
L, E, A, Daa = pyverbplt.load_plt('path/to/file.plt')

# Example 2: Load data from a .plt file but only unpack one variable
_, _, _, Daa = pyverbplt.load_plt('path/to/file.plt')

# Example 3: Load data from a .plt file into a single variable with specific zones
psd = pyverbplt.load_plt('path/to/file.plt', first_zone=2, n_zones=5, skip_zones=2)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.
