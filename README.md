# GeneMap2-Parser

## Overview

This script parses the `genemap2.txt` file from [OMIM](https://omim.org/) and extracts gene-related data, including phenotypes and inheritance information. The parsed output is serialized into a `.pickle` file.

## Installation

```shell
pip install git+https://github.com/OMIM-org/genemap2-parser.git
```


## Usage

```bash
parseGeneMap2 -i path/to/genemap2.txt -o path/to/output/
```

### Arguments

- `-i, --input_file`  (Required) Path to `genemap2.txt`
- `-o, --output_path` (Optional) Output directory (default: current directory)

### Example:

```bash
parseGeneMap2 -i genemap2.txt -o output_dir/
```

## Output

A `output.pickle` file containing extracted gene and phenotype data is created in the specified directory. To read:

```python
import pickle
with open("output_dir/output.pickle", "rb") as f:
    data = pickle.load(f)
print(data[:5])  # First 5 entries
```

## Useful Links

- [OMIM](https://omim.org/)
- [OMIM Downloads](https://omim.org/downloads)
