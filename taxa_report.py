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
    with open(file_path, 'r') as file:
        lines = file.readlines()

    filtered_lines = [
        line for line in lines
        if not (line.split()[0] == '0.00' and line.split()[1] == '0' and line.split()[2] == '0')
    ]

    sorted_lines = sorted(
        filtered_lines,
        key=lambda x: (float(x.split()[0]), int(x.split()[1])),
        reverse=True
    )
    with open(file_path, 'w') as file:
        file.writelines(sorted_lines)

def trim_report(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()

    filtered_lines = []
    for line in lines:
        parts = line.split("\t")
        try:
            percentage = float(parts[0].strip())
            if percentage > 0.00:
                filtered_lines.append(line)
        except (ValueError, IndexError):
            continue

    with open(file_path, 'w') as outfile:
        outfile.writelines(filtered_lines)

def parse_kraken_report(file_path):
    root_id = '1'
    hierarchy = {}
    parents = []

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 6:
            continue

        level = len(parts[5]) - len(parts[5].lstrip())
        tax_id = parts[4].strip()
        name = parts[5].strip()
        full_name = f"{name.replace(' ', '_').replace(':', '_')}:{tax_id}"

        while parents and level <= parents[-1][0]:
            parents.pop()

        if parents:
            parent_level, parent_id = parents[-1]
            hierarchy[parent_id]['children'].append(tax_id)
        else:
            parent_id = None

        hierarchy[tax_id] = {'name': full_name, 'children': []}
        parents.append((level, tax_id))

    return hierarchy

def build_newick(hierarchy, node):
    if not hierarchy[node]['children']:
        return hierarchy[node]['name']
    children = [build_newick(hierarchy, child) for child in hierarchy[node]['children']]
    return f"({','.join(children)}){hierarchy[node]['name']}"

def process_kraken_report(file_path):
    try:
        hierarchy = parse_kraken_report(file_path)
        newick_tree = build_newick(hierarchy, '1') + ';'
        

        output_file = os.path.splitext(file_path)[0] + ".newick"
        with open(output_file, 'w') as f:
            f.write(newick_tree)
        
        return output_file  
    except Exception as e:
        print(f"Došlo k chybě při zpracování souboru {file_path}: {e}")
        return None

def load_percentages(trimmed_file):
    percentages = {}
    with open(trimmed_file, 'r') as f:
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 6:
                try:
                    percentage = float(parts[0].strip())
                    name = parts[5].strip()
                    percentages[name] = percentage
                except ValueError:
                    continue
    return percentages

def simplify_tree_labels(tree, percentages):
    for clade in tree.find_clades():
        if clade.is_terminal():
            clade_name = clade.name or ""
            clade_name_normalized = clade_name.replace(" ", "_").lower()
            for name, percentage in percentages.items():
                name_normalized = name.replace(" ", "_").lower()
                if name_normalized in clade_name_normalized:
                    clade.name = f"{clade_name} ({percentage}%)"
                    break
        else:
            clade.name = ""

def generate_phylogenetic_tree(newick_file, trimmed_file):
    directory = os.path.dirname(newick_file)
    today_date = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"{today_date}-tree.png"
    output_path = os.path.join(directory, output_filename)

    if newick_file and trimmed_file:
        percentages = load_percentages(trimmed_file)

        try:
            tree = Phylo.read(newick_file, "newick")
            simplify_tree_labels(tree, percentages)

            num_leaves = sum(1 for _ in tree.get_terminals())
            fig_width = 8
            fig_height = max(8, num_leaves * 0.3)

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            plt.rcParams["font.size"] = max(6, 12 - (num_leaves // 10))

            ax.margins(0.2, 0.2)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            Phylo.draw(tree, do_show=False, axes=ax, show_confidence=False)

            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close(fig)

            print(f"Strom byl uložen do {output_path}")
            return output_path
        except Exception as e:
            print(f"Chyba při zpracování souboru {newick_file}: {e}")
    else:
        print("Nebyl nalezen požadovaný soubor.")
        return None

def parse_file(file_path):
    data = []
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
            rank = rank.strip()
            name = name.strip()
            
            unique_entries[taxid] = [percentage, count, taxid, rank, tax_num, name]
            
            if name in domains:
                domains[name] += percentage
    
    df = pd.DataFrame(unique_entries.values(), columns=["Percentage", "Count", "TaxID", "Rank", "TaxNum", "Name"])
    df.sort_values(by="Percentage", ascending=False, inplace=True)
    df_domains = pd.DataFrame(list(domains.items()), columns=["Domain", "Percentage"])
    
    return df_domains, df

def generate_html_table(df, title):
    table_html = df.to_html(index=False, classes="table table-bordered", escape=False)
    return f"<h2>{title}</h2>" + table_html

def save_html(file_path, df_domains, df_all):
    html_content = """
    <html>
    <head>
        <title>Taxonomy Report</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body class="container">
    """
    html_content += generate_html_table(df_domains, "Domain Table")
    html_content += generate_html_table(df_all, "Conclusion")
    html_content += "</body></html>"
    
    soup = BeautifulSoup(html_content, "html.parser")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

    return file_path

def process_trimmed_report(trimmed_report_path):
    if not os.path.exists(trimmed_report_path):
        return

    df_domains, df_all = parse_file(trimmed_report_path)

    output_file = f"{str(pd.Timestamp.today().date())}-taxonomy-report.html"
    save_html(output_file, df_domains, df_all)

    print(f"HTML report saved as {output_file}")
    return output_file

def generate_html_report(image_path, html_table_file,sample_name):
    if not os.path.exists(image_path) or not os.path.exists(html_table_file):
        print("File not found.")
        return
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(html_table_file, "r", encoding="utf-8") as f:
        table_data_html = f.read()
    
    img_base64 = ""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    output_html = "report_page.html"
    
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
        <p>Created: {timestamp}</p>
        <img src="data:image/png;base64,{img_base64}" alt="Tree">
        
        {table_data_html}
    </body>
    </html>
    """
    
    with open(output_html, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"File created: {output_html}")

def parse_args():
    parser = argparse.ArgumentParser(description="Process Kraken2 report and generate taxonomy outputs.")
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the Kraken2 report file."
    )
    parser.add_argument(
        "-s", "--sample_name",
        required=True,
        help="Name of the sample."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    kraken_report_path = args.input
    sample_name = args.sample_name  

    filter_and_sort_file(kraken_report_path)
    trim_report(kraken_report_path)    
    newick_tree = process_kraken_report(kraken_report_path)  
    tree_image_path = generate_phylogenetic_tree(newick_tree, kraken_report_path) 
    domain_table = process_trimmed_report(kraken_report_path)  
    generate_html_report(tree_image_path, domain_table,sample_name) 

    
if __name__ == "__main__":   
    sys.exit(main())
