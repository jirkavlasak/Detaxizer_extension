#! /usr/bin/env python

import os
from datetime import datetime
import sys
from Bio import Phylo
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import base64
import argparse

def filter_and_sort_file(file_path):
    """
    Input:
        file_path (str): Path to the Kraken2 report file.
    Output:
        None (overwrites the input file).
    Description:
        Removes lines with zero values and sorts the file by percentage and count in descending order.
    """
    with open(file_path, 'r') as file:
        lines = [line for line in file if not (line.split()[0] == '0.00' and line.split()[1] == '0' and line.split()[2] == '0')]
    lines.sort(key=lambda x: (float(x.split()[0]), int(x.split()[1])), reverse=True)
    with open(file_path, 'w') as file:
        file.writelines(lines)

def trim_report(file_path):
    """
    Input:
        file_path (str): Path to the Kraken2 report file.
    Output:
        None (overwrites the input file).
    Description:
        Removes lines where the classification percentage is 0.00.
    """
    with open(file_path, 'r') as infile:
        lines = [line for line in infile if (len(line.split("\t")) > 0 and float(line.split("\t")[0].strip()) > 0.00)]
    with open(file_path, 'w') as outfile:
        outfile.writelines(lines)

def parse_kraken_report(file_path):
    """
    Input:
        file_path (str): Path to the Kraken2 report file.
    Output:
        hierarchy (dict): Dictionary representing the taxonomic hierarchy.
    Description:
        Parses the Kraken2 report and builds a tree structure (hierarchy) of taxa.
    """
    hierarchy, parents = {}, []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 6 or parts[3] == 'U' or parts[4] in ('2787854', '28384'):
                continue
            level = len(parts[5]) - len(parts[5].lstrip())
            tax_id, name, rank = parts[4].strip(), parts[5].strip(), parts[3].strip()
            while parents and level <= parents[-1][0]:
                parents.pop()
            if parents:
                hierarchy[parents[-1][1]]['children'].append(tax_id)
            hierarchy[tax_id] = {'name': name.replace(' ', '_').replace(':', '_') + ':1', 'children': [], 'rank': rank}
            parents.append((level, tax_id))
    return hierarchy

def build_newick(hierarchy, node, is_root=True):
    """
    Input:
        hierarchy (dict): Taxonomic tree structure.
        node (str): Current node (tax_id).
        is_root (bool): Whether this is the root node.
    Output:
        newick (str): Subtree in Newick format.
    Description:
        Recursively converts the tree structure to Newick format.
    """
    if not hierarchy[node]['children']:
        return hierarchy[node]['name']
    children = [build_newick(hierarchy, child) for child in hierarchy[node]['children']]
    return f"({','.join(children)}){hierarchy[node]['name']}" if is_root else f"({','.join(children)})"

def process_kraken_report(file_path):
    try:
        hierarchy = parse_kraken_report(file_path)
        newick_tree = build_newick(hierarchy, '1') + ';'
        output_file = os.path.splitext(file_path)[0] + ".newick"
        with open(output_file, 'w') as f:
            f.write(newick_tree)
        return output_file
    except Exception as e:
        print(f"Error occurred while loading the file {file_path}: {e}")
        return None

def load_percentages(trimmed_file):
    """
    Input:
        trimmed_file (str): Path to the trimmed Kraken2 report file.
    Output:
        percentages (dict): Dictionary mapping taxon names to (percentage, taxonomic_rank).
    Description:
        Loads classification percentages and taxonomic ranks for each taxon from the trimmed report.
    """
    percentages = {}
    with open(trimmed_file, 'r') as f:
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 6:
                try:
                    percentage = float(parts[0].strip())
                    taxonomic_rank = parts[3].strip()
                    name = parts[5].strip()
                    percentages[name] = (percentage, taxonomic_rank)
                except ValueError:
                    continue
    return percentages

def simplify_tree_labels(tree, percentages):
    """
    Input:
        tree (Bio.Phylo.BaseTree.Tree): Phylogenetic tree object.
        percentages (dict): Dictionary mapping taxon names to (percentage, taxonomic_rank).
    Output:
        None (modifies the tree in place).
    Description:
        Updates terminal clade labels to include percentage and taxonomic rank.
        Sets internal node labels to empty.
    """
    for clade in tree.find_clades():
        if clade.is_terminal():
            clade_name = clade.name or ""
            clade_name_normalized = clade_name.replace(" ", "_").lower()
            for name, (percentage, taxonomic_rank) in percentages.items():
                if name.replace(" ", "_").lower() == clade_name_normalized:
                    clade.name = f"{clade_name} ({percentage}%, {taxonomic_rank})"
                    break
        else:
            clade.name = ""


def generate_phylogenetic_tree(newick_file, trimmed_file):
    """
    Input:
        newick_file (str): Path to the Newick tree file.
        trimmed_file (str): Path to the trimmed Kraken2 report file.
    Output:
        output_path (str): Path to the saved PNG image of the tree, or None on error.
    Description:
        Loads a phylogenetic tree from a Newick file, annotates leaf labels with percentages and ranks,
        draws the tree using matplotlib, and saves it as a PNG image. The Y axis is set to show all leaves,
        and the axis is inverted so that leaf 1 is at the top.
    """
    directory = os.path.dirname(newick_file)
    output_path = os.path.join(directory, f"{datetime.now().strftime('%Y-%m-%d')}-tree.png")
    if not (newick_file and trimmed_file):
        print("Required file not found.")
        return None
    try:
        tree = Phylo.read(newick_file, "newick")
        simplify_tree_labels(tree, load_percentages(trimmed_file))
        num_leaves = sum(1 for _ in tree.get_terminals())
        fig, ax = plt.subplots(figsize=(8, max(8, num_leaves * 0.3)))
        plt.rcParams["font.size"] = max(6, 12 - (num_leaves // 10))
        ax.margins(0.2, 0.2)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        Phylo.draw(tree, do_show=False, axes=ax, show_confidence=True, label_func=lambda clade: clade.name)
        ax.set_xlabel("Taxonomic Rank Based Distance")
        ax.set_ylabel("Number of Taxa")
        ax.set_yticks(range(1, num_leaves + 1, 1))
        ax.invert_yaxis()
        ax.set_title("Phylogenetic Tree", fontsize=14, fontweight='bold', color='darkblue')
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"Tree saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error processing file {newick_file}: {e}")

def parse_file(file_path):
    """
    Input:
        file_path (str): Path to the trimmed Kraken2 report file.
    Output:
        df_domains (pd.DataFrame): Table with domain names and their percentages.
        df (pd.DataFrame): Table with all unique taxonomic entries and their statistics.
    Description:
        Parses the trimmed Kraken2 report and summarizes domain-level percentages and all unique entries.
        Returns two dataframes: one for domains, one for all entries.
    """
    domains = {"Eukaryota": 0, "Bacteria": 0, "Archaea": 0}
    unique_entries = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) < 6:
                continue
            percentage, count, taxid, rank, tax_num, name = parts
            percentage = float(percentage)
            count = int(count)
            taxid = int(taxid)
            unique_entries[taxid] = [percentage, count, taxid, rank.strip(), tax_num, name.strip()]
            if name.strip() in domains:
                domains[name.strip()] += percentage
    df = pd.DataFrame(unique_entries.values(), columns=["Percentage", "Count", "Assigned directly", "Rank", "TaxID", "Name"])
    df.sort_values(by="Percentage", ascending=False, inplace=True)
    df_domains = pd.DataFrame(list(domains.items()), columns=["Domain", "Percentage"])
    return df_domains, df

def generate_html_table(df, title):
    """
    Input:
        df (pd.DataFrame): DataFrame to be rendered as HTML table.
        title (str): Title for the table.
    Output:
        html (str): HTML string with the table and title.
    Description:
        Converts a pandas DataFrame into a styled HTML table with a heading.
    """
    return f"<h2>{title}</h2>" + df.to_html(index=False, classes="table table-bordered", escape=False)

def save_html(file_path, df_domains, df_all):
    """
    Input:
        file_path (str): Path to the output HTML file.
        df_domains (pd.DataFrame): DataFrame with domain summary.
        df_all (pd.DataFrame): DataFrame with all taxonomic entries.
    Output:
        file_path (str): Path to the saved HTML file.
    Description:
        Generates a simple HTML report with two tables (domains and all entries) and saves it to disk.
    """
    html_content = f"""
    <html>
    <head>
        <title>Taxonomy Report</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="container">
        {generate_html_table(df_domains, "Domain Table")}
        {generate_html_table(df_all, "Conclusion")}
    </body></html>
    """
    soup = BeautifulSoup(html_content, "html.parser")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())
    return file_path

def process_trimmed_report(trimmed_report_path):
    """
    Input:
        trimmed_report_path (str): Path to the trimmed Kraken2 report file.
    Output:
        output_file (str): Path to the saved HTML report.
    Description:
        Parses the trimmed report, generates summary tables, and saves an HTML report.
    """
    if not os.path.exists(trimmed_report_path):
        return
    df_domains, df_all = parse_file(trimmed_report_path)
    output_file = f"{str(pd.Timestamp.today().date())}-taxonomy-report.html"
    save_html(output_file, df_domains, df_all)
    print(f"HTML report saved as {output_file}")
    return output_file

def generate_html_report(image_path, html_table_file, sample_name):
    """
    Input:
        image_path (str): Path to the PNG image of the tree.
        html_table_file (str): Path to the HTML table file.
        sample_name (str): Name of the sample.
    Output:
        None (creates an HTML report file).
    Description:
        Generates a final HTML report with the tree image and tables, and saves it to disk.
    """
    if not os.path.exists(image_path) or not os.path.exists(html_table_file):
        print("File not found.")
        return
    with open(html_table_file, "r", encoding="utf-8") as f:
        table_data_html = f.read()
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    html_content = f"""
    <!DOCTYPE html>
    <html lang="cs">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{sample_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
            img {{ max-width: 100%; height: auto; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>{sample_name}</h1>
        <p>Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <img src="data:image/png;base64,{img_base64}" alt="Tree">
        {table_data_html}
    </body>
    </html>
    """
    with open("report_page.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    print("File created: report_page.html")

def parse_args():
    """
    Input:
        None (reads from sys.argv).
    Output:
        args (argparse.Namespace): Parsed command-line arguments.
    Description:
        Parses command-line arguments for input file and sample name.
    """
    parser = argparse.ArgumentParser(description="Process Kraken2 report and generate taxonomy outputs.")
    parser.add_argument("-i", "--input", required=True, help="Path to the Kraken2 report file.")
    parser.add_argument("-s", "--sample_name", required=True, help="Name of the sample.")
    return parser.parse_args()

def main():
    """
    Input:
        None (uses command-line arguments).
    Output:
        None (runs the full workflow).
    Description:
        Main workflow: processes Kraken2 report, generates tree and tables, and creates HTML reports.
    """
    args = parse_args()
    filter_and_sort_file(args.input)
    trim_report(args.input)
    newick_tree = process_kraken_report(args.input)
    tree_image_path = generate_phylogenetic_tree(newick_tree, args.input)
    domain_table = process_trimmed_report(args.input)
    generate_html_report(tree_image_path, domain_table, args.sample_name)

if __name__ == "__main__":
    sys.exit(main())
