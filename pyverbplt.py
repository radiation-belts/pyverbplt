import numpy as np
# from collections import namedtuple

def load_plt(filename, permute=True, squeeze=False, make3D=False, varout=True,
             first_zone=1, n_zones=None, skip_zones=0, nozone=False):
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

    first_zone : int, optional (default=1)
        TODO: Specifies the first zone in the plt file to begin loading data from.

    n_zones : int or None, optional (default=None)
        TODO: Specifies the number of zones to load from the plt file. If None, all zones will be loaded.

    skip_zones : int, optional (default=0)
        TODO: Specifies the number of zones to skip before starting to load data.

    nozone : bool, optional (default=False)
        TODO: If True, does not consider zones while loading data. All data will be loaded as a single block.

    Returns
    -------
    data : list of dictionaries or tuple of dictionaries
        The loaded data structured in dictionaries. Each dictionary represents a variable and contains
        fields such as name, arr (the data array), size1, size2, size3 (dimensions of the array), and comment - lines from plt files that start with #.

        If varout is True and multiple variables are present, a tuple  is returned.

    Raises
    ------
    warnings.Warn
        If the specified plt file does not exist.

        Examples
    --------
    Example 1: Loading multiple variables from a plt file and unpacking them into separate variables
    >>> L, E, A, Daa = pyverbplt.load_plt(filename)

    In this example, data from the specified plt file is loaded into four variables: L, E, A, Daa. Each variable
    corresponds to a different variable present in the plt file.

    Example 2: Loading data from the same plt file but only unpacking one variable
    >>> _, _, _, Daa = pyverbplt.load_plt(filename)

    Here, data from the plt file is again loaded, but only the last variable (Daa2) is unpacked and the rest are
    ignored using underscores (_).

    Example 3: Loading data from a different plt file into a single variable
    >>> psd = pyverbplt.load_plt(filename)

    In this example, data from another plt file is loaded into a single variable (psd). Since only one variable is
    specified, it assumes that either the plt file has only one variable, or you are interested in loading
    data as a tuple.
    """

    import os
    import warnings

    if not os.path.isfile(filename):
        warnings.warn(f"File {filename} does not exist")
        return

    print("Scanning file for number of zones")
    zones, zone_lines, n = _scan_plt_zones(filename)
    print(f"{len(zones)} zones found")

    # If there are no zones, we set the first line to be ZONE
    if len(zones) == 0:
        zones = 0
        zone_lines = [""]
        # TODO: make correct conditions on the file with no zones
        return

    # Read the file
    with open(filename, 'r') as file:

        # Read content until first zone
        lines = [file.readline() for _ in range(zones[0])]

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
                variables = line.split('=')[1].strip().replace('"', '').split(', ')
                continue

        # TODO: Stop if variables were not found

        # Read file zone by zone
        first_zone = False
        for z in range(len(zones)):
            print(zone_lines[z])

            if not first_zone:
                first_zone = True
                zone_info = zone_lines[z].replace(',', '').split(' ')

                # Extract dimensions from zone info
                dimensions = [int(d.split('=')[1]) for d in zone_info[2:]]

                # Read number of lines that correspond to the product of dimensions
                lines_number = np.prod(dimensions)

                # This creates immutable object which we cannot change after it is created
                # # Create data structure using namedtuple
                # Plt_Variable = namedtuple('Plt_Variable', ['name', 'arr', 'size1', 'size2', 'size3', 'comment'])
                # data = []
                # for var in variables:
                #     data.append(Plt_Variable(name=var, arr=np.zeros((len(zones), *dimensions)), comment=comments,
                #                              size1=dimensions[0], size2=dimensions[1], size3=dimensions[2]))

                # Create data structure using dictionary
                data = []
                for var in variables:
                     data.append(dict(name=var, arr=np.zeros((len(zones), *dimensions)), comment=comments,
                                      size1=dimensions[0], size2=dimensions[1], size3=dimensions[2]))

            # Read data
            file.readline()  # Skip zone
            lines = [file.readline() for _ in range(lines_number)]
            data_zone = np.loadtxt(lines)

            if data_zone.ndim == 1:
                data[0]["arr"][z, :] = data_zone.reshape(dimensions)
            else:
                for v in range(len(variables)):
                    data[v]["arr"][z, :] = data_zone[:, v].reshape(dimensions)

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
