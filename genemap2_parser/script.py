import re
import argparse
import multiprocessing
import pickle
from pathlib import Path
from typing import Optional, Dict, List, Any

def process_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Processes a single line from the genemap2 file.
    
    :param line: A single line of text from the file
    :return: A dictionary containing extracted data or None if the line is invalid
    """
    if line.startswith('#') or not line.strip():
        return None
    
    value_list = line.strip().split('\t')
    if len(value_list) < 14:
        return None
    
    try:
        chromosome, genomic_position_start, genomic_position_end, cyto_location, computed_cyto_location, mim_number, \
        gene_symbols, gene_name, approved_gene_symbol, entrez_gene_id, ensembl_gene_id, comments, phenotype_string, mouse = value_list
    except ValueError:
        raise ValueError(f"Unexpected number of columns in line: {line}")
    
    if not phenotype_string:
        return None
    
    phenotypes = []
    for phenotype in phenotype_string.split(';'):
        phenotype = phenotype.strip()
        matcher = re.match(r'^(.*),\s(\d{6})\s\((\d)\)(|, (.*))$', phenotype)
        
        if matcher:
            phenotype_name = matcher.group(1)
            phenotype_mim_number = matcher.group(2)
            phenotype_mapping_key = matcher.group(3)
            inheritances = matcher.group(5).split(', ') if matcher.group(5) else []
        else:
            matcher = re.match(r'^(.*)\((\d)\)(|, (.*))$', phenotype)
            if matcher:
                phenotype_name = matcher.group(1)
                phenotype_mim_number = None
                phenotype_mapping_key = matcher.group(2)
                inheritances = matcher.group(4).split(', ') if matcher.group(4) else []
            else:
                continue
        
        phenotypes.append({
            'name': phenotype_name,
            'mim_number': phenotype_mim_number,
            'mapping_key': phenotype_mapping_key,
            'inheritance': inheritances
        })
    
    return {
        'chromosome': chromosome,
        'genomic_position_start': genomic_position_start,
        'genomic_position_end': genomic_position_end,
        'cyto_location': cyto_location,
        'computed_cyto_location': computed_cyto_location,
        'mim_number': mim_number,
        'gene_symbols': gene_symbols,
        'gene_name': gene_name,
        'approved_gene_symbol': approved_gene_symbol,
        'entrez_gene_id': entrez_gene_id,
        'ensembl_gene_id': ensembl_gene_id,
        'comments': comments,
        'mouse': mouse,
        'phenotypes': phenotypes
    }

def parse_genemap2(filename: Path) -> List[Dict[str, Any]]:
    """
    Parses the genemap2 file and extracts relevant data.
    
    :param filename: Path to the genemap2.txt file
    :return: A list of dictionaries containing parsed data
    """
    try:
        with filename.open('r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file '{filename}' not found.")
    except IOError as e:
        raise IOError(f"Error reading file '{filename}': {e}")
    
    with multiprocessing.Pool() as pool:
        parsed_data = pool.map(process_line, lines)
    
    return [entry for entry in parsed_data if entry]

def main():
    """Main"""
    parser = argparse.ArgumentParser(
        description=(
            "This is a simple script to parse the genemap2.txt file that "
            "can be downloaded from https://omim.org/\n\n"
            "The file can be downloaded from https://omim.org/downloads "
            "(registration required)."
        )
    )
    parser.add_argument("--input_file", "-i", type=str, required=True, help="Path to the genemap2.txt file.")
    parser.add_argument("--output_path", "-o", type=str, default=".", help="Path to write the serialized parsed data (default: %(default)s).")
    args = parser.parse_args()
    
    input_file = Path(args.input_file)
    output_path = Path(args.output_path)
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
    
    if not input_file.is_file():
        raise ValueError(f"Specified input path '{input_file}' is not a valid file.")
    
    if input_file.suffix != ".txt":
        raise ValueError(f"Expected a .txt file but got '{input_file.suffix}' instead.")
    
    if not output_path.exists():
        raise FileNotFoundError(f"Output path '{output_path}' does not exist.")
    
    if not output_path.is_dir():
        raise ValueError(f"Specified output path '{output_path}' is not a directory.")
    
    parsed_data = parse_genemap2(input_file)
    
    try:
        with (output_path / "output.pickle").open('wb') as file:
            pickle.dump(parsed_data, file)
    except IOError as e:
        raise IOError(f"Error writing output file: {e}")


if __name__ == "__main__":
    main()