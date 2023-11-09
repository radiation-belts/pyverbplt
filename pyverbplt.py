import numpy as np
import re

def load_plt(filename, permute=True, squeeze=False, make3D=False, varout=True,
             first_zone=0, n_zones=None, skip_zones=0):
    """
    Load data from a plt file into structured numpy arrays.

    Parameters
    ----------
    filename : str
        The path to the plt file to be loaded.

    permute : bool, optional (default=True)
        If True, permutes the array axes of the loaded data. The permutation
        sequence used is [1, 2, 3] -> [3, 2, 1].

    squeeze : bool, optional (default=False)
        If True, removes single-dimensional entries from the shape of the loaded data.

    make3D : bool, optional (default=False)
        If True, moves the first axis of the loaded data to the last, making the data 3D.
        Since first dimension is time, can be usefully for loading diffusion coefficients

    varout : bool, optional (default=True)
        If True, returns the loaded data as a tuple instead of a list.
        The tuple correspond to the variables in the plt file.

    first_zone : int, optional (default=0)
        Specifies the first zone in the plt file to begin loading data from, starts with 0

    n_zones : int or None, optional (default=None)
        Specifies the number of zones to load from the plt file. If None, all zones will be loaded.

    skip_zones : int, optional (default=0)
        Specifies the number of zones to skip before loading next zone.

    Returns
    -------
    data : list of dictionaries or tuple of dictionaries
        The loaded data structured in dictionaries. Each dictionary represents a variable and contains
        fields such as name, arr (the data array), size1, size2, size3 (dimensions of the array), and comment - lines from plt files that start with #.

        If varout is True and multiple variables are present, a tuple  is returned.

    Raises
    ------
    warnings.Warn
        - If the specified plt file does not exist.
        - If the specified first_zone is greater than the available zones in the plt file
        - If there are no zones available to read due to user specifications such as zone skipping or
          specific zone loading (first_zone, n_zones, skip_zones)
        - If variables were not found in the header of the file.

    Examples
    --------
    Example 1: Loading multiple variables from a plt file and unpacking them into separate variables
    >>> L, E, A, Daa = pyverbplt.load_plt(filename)

    In this example, data from the specified plt file is loaded into four variables: L, E, A, Daa. Each variable
    corresponds to a different variable present in the plt file.

    Example 2: Loading data from a plt file but only unpacking one variable Daa
    >>> _, _, _, Daa = pyverbplt.load_plt(filename)

    Here, data from the plt file is again loaded, but only the last variable (Daa) is unpacked and the rest are
    ignored using underscores (_).

    Example 3: Loading data from a plt file into a single variable
    >>> psd = pyverbplt.load_plt(filename, first_zone=2, n_zones=5, skip_zones=2)

    In this example, data from a plt file is loaded into a single variable (psd), specifying which zones to load using
    the parameters first_zone, n_zones, and skip_zones. The function starts loading data from the second zone (first_zone=2),
    loads up to five zones (n_zones=5), and skips every two zones (skip_zones=2). Since only one variable is specified,
    it assumes that either the plt file has only one variable, or you are interested in loading data as a tuple.
    """

    import os
    import warnings

    if not os.path.isfile(filename):
        warnings.warn(f"File {filename} does not exist")
        return

    print("Scanning file for the number of zones")
    zones, zone_lines, n = _scan_plt_zones(filename)
    print(f"{len(zones)} zones found")

    # First zone in case we need to skip zones
    zone_0 = zones[0]

    # Implementing zone skipping
    if first_zone > len(zones):
        warnings.warn("first_zone is greater than the number of available zones")
        return

    # Adjusting the zones according to the first_zone, n_zones, and skip_zones
    zones = zones[first_zone:]
    zone_lines = zone_lines[first_zone:]

    if n_zones is not None:
        zones = zones[:n_zones * (skip_zones + 1):skip_zones + 1]
        zone_lines = zone_lines[:n_zones * (skip_zones + 1):skip_zones + 1]
    else:
        zones = zones[::skip_zones + 1]
        zone_lines = zone_lines[::skip_zones + 1]

    if len(zones) == 0:
        warnings.warn("No zones available to read")
        return

    # Read the file
    line_counter = 0
    with open(filename, 'r') as file:

        # Read content until first zone
        lines = [file.readline() for _ in range(zone_0 + 1)]
        line_counter = zone_0 + 1

        # Parsing header
        comments = []
        variables = []
        for line in lines:
            line = line.strip()

            # Reading comments that start with #
            if line.startswith('#'):
                comments.append(line)
                continue

            # Reading VARIABLES line
            if 'VARIABLES' in line:
                variables_line = line.split('=')[1].strip()
                # Use regular expression to find the variables, becuase it is more relaiable
                variables = re.findall(r'"([^"]*)"', variables_line)
                continue

        # Stop if variables were not found
        if len(variables) == 0:
            warnings.warn("VARIABLES line not found")
            return

        # Read file zone by zone
        for z in range(len(zones)):
            # New line is on zone_lines
            print(f"{z+1}/{len(zones)}: {zone_lines[z]}", end='')
            zone_info = zone_lines[z].replace(',', '').split()

            # Only from the first zone
            if z == 0:

                # Extract dimensions from zone info
                dimensions = [int(d.split('=')[1]) for d in zone_info[2:]]

                # Read number of lines that correspond to the product of dimensions
                lines_number = np.prod(dimensions)

                # Create data structure using dictionary
                data = []
                for var in variables:
                    data.append(dict(name=var, arr=np.zeros((len(zones), *dimensions)), comment=comments,
                                     size1=dimensions[0], size2=dimensions[1], size3=dimensions[2],
                                     zone=list()))

            # Skip zones
            for _ in range(zones[z] - line_counter + 1):
                file.readline()  # Skip zone

            # Read data
            lines = [file.readline() for _ in range(lines_number)]
            data_zone = np.loadtxt(lines)
            line_counter = zones[z] + lines_number + 1

            T = zone_info[1].split('=')[1].replace('"', '')

            if data_zone.ndim == 1:
                data[0]["arr"][z, :] = data_zone.reshape(dimensions)
                data[0]["zone"].append(T)
            else:
                for v in range(len(variables)):
                    data[v]["arr"][z, :] = data_zone[:, v].reshape(dimensions)
                    data[v]["zone"].append(T)

    # Apply options
    for v in range(len(variables)):
        if permute:
            data[v]["arr"] = np.moveaxis(data[v]["arr"], [1, 2, 3], [3, 2, 1])
            data[v]["size1"] = dimensions[2]
            data[v]["size2"] = dimensions[1]
            data[v]["size3"] = dimensions[0]

        if make3D:
            data[v]["arr"] = np.moveaxis(data[v]["arr"], 0, 3)

        if squeeze:
            data[v]["arr"] = np.squeeze(data[v]["arr"])

    # Return data as a tuple instead of a list
    if varout:
        if len(variables) == 1:
            data = data[0]
        else:
            data = tuple(data)

    return data


def _scan_plt_zones(filename):
    """
    Scan a plt file and identify the lines containing the keyword "ZONE", recording their line numbers and the full content of these lines.

    Parameters:
    filename (str): The name of the plt file to be scanned.

    Returns:
    tuple: A tuple containing three elements:
        - list of integers: Line numbers where the keyword "ZONE" appears.
        - list of strings: The full content of the lines where the keyword "ZONE" appears.
        - integer: The zero-based index of the last line in the file.

    Note:
    - The function reads the file line by line, checking for the existence of the keyword "ZONE".
    - Line numbers are zero-based, meaning the first line is line 0.
    - The function is case-sensitive, and will not recognize "zone" or other case variations.

    Example:
    >>> zones, lines, n = _scan_plt_zones('example.plt')
    """
    zones = []
    lines = []
    with open(filename, 'r') as file:
        for i, line in enumerate(file):
            if "ZONE" in line:
                zones.append(i)
                lines.append(line)

    return zones, lines, i
