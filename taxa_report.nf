process TAXA_REPORT {
    tag "$meta.id"
    label 'process_medium'

    conda "conda-forge::python=3.12.0 biopython=1.81 pandas=2.1.1 matplotlib=3.8.0 beautifulsoup4=4.12.2"
    
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/biopython:1.81' :
        'biocontainers/biopython:1.81' }"

    input:
    tuple val(meta), path(kraken_report), val(sample_name)
    

    output:
    tuple val(meta), path('*-tree.png'), emit: tree_image
    tuple val(meta), path('*-taxonomy-report.html'), emit: html_report
    path "versions.yml", emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    """
    taxa_report.py -i $kraken_report -s $sample_name

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
        biopython: \$(python -c "import pkg_resources; print(pkg_resources.get_distribution('biopython').version)")
        pandas: \$(python -c "import pandas as pd; print(pd.__version__)")
        matplotlib: \$(python -c "import matplotlib; print(matplotlib.__version__)")
        beautifulsoup4: \$(python -c "import bs4; print(bs4.__version__)")
    END_VERSIONS
    """
}
