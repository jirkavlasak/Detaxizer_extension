# Detaxizer_extension
This project is based on my bachelor thesis, where my goal was to find sufficent nf-core based pipeline, which is possible to edit and implement new porcesses, specially to find contaminations in sequacing data adn create HTML page report about sample.
All files you can find here are not part of the original Detaxizer pipeline, but will help you to implement new process to the pipeline and I will provide here to you a little guid how to do so.
But first, please be sure your Detaxize pipeline is installed correctly.
Link to official site of Detaxizer pipeline: https://nf-co.re/detaxizer/1.0.0/

## ABOUT
### You can modify taxa_report.py to meet your criteria
Main focus here is on taxa_report.py and taxa_report.nf. These scripts are new additional process for Detaxizer pipeline. Script take input from kraken2 classification report and original name of sample given in sample sheet. Scripts return phylogenetic tree of classifed taxons in kraken2 classification report and HTML report page with summary of that classification. Note that taxa_report.py filters lines where taxons had zero values at classification, sorts lines by percentage values and trimms taxons that their classification value was to loo to considre tham as rightfully classifed and are most likley some kind of buzz. 
<p align="center">
  <img src="https://github.com/user-attachments/assets/16ae2d6b-abde-4fb2-909c-6c3010def4e3" alt="Popis obrázku" width="300"/>
</p>



## CONFIGURATION
If you managed to download and install Detaxizer pipeline, you should firstly look at configuration settings, it is set by default that you gotta have at least 32GB RAM and 8CPUs ready for the run. If you do not have these technological parameters on your machine or you just do not want to go with this configuration, you can create or use mine (you can find it in repository named as 'custom.config'). After creating this configurations, you have add -c parameter while laucnhing pipeline. For example if I run pipeline with my custom.config file I add to command  .... -c path\to\custom.config

## IMPLEMNTING TAXA REPORT 
If you want to add Taxa report to the Detaxizer pipeline, at first you should add taxa_report.py to ~\detaxizer\bin folder and continue with adding taxa_report.nf to ~\detaxizer\modules\local. If you managed to do all that your are almost done! One of the last step is to include newly created module into ~detaxier\workflows\detaxier.nf as include { TAXA_REPORT } from '../modules/local/taxa_report'. With all that you have to add process. I recommend putting TAXA_REPORT porcess right before SUMMARY_CLASIFICATION process to keep analytic and summary parts separated, but it is up to you, note that there is limitation where you can put it and is that you can put the TAXA_REPORT process only below KRAKEN2_KRANE2 process, beacuse TAXA_REPORT needs input that is made by KRAKEN2_KRAKEN2. 

### TAXA_REPORT PROCESS
Here below is process to be add as described earlier in IMPLEMETING TAXA REPORT part 

    TAXA_REPORT(
        KRAKEN2_KRAKEN2.out.report.map { meta, path ->
               return [meta, path, meta.id] 
                            }
        )
        ch_versions = ch_versions.mix(TAXA_REPORT.out.versions.first())
        ch_taxa_tree = TAXA_REPORT.out.tree_image
        ch_taxa_html = TAXA_REPORT.out.html_report

## WORK ENVIRONMENT
I recommend to keep all samples, sample sheets, workdir and outdir in the same directory for better manipulation. For example I obtained 24 human samples and 25th mouse sample. For each sample I created folder named as sample. Inside that folder I kept sample sheet, sample data, workdir and outdir, below is simple schema for better visualization. 

<pre> ``` MAIN_FOLDER --> SAMPLE1 samplesheet.csv sample.fastq.gz WORKDIR OUTDIR SAMPLE2 ... ``` </pre>

MAIN_FOLDER -->
 SAMPLE1
  samplesheet.csv
  sample.fastq.gz
  WORKDIR
  OUTDIR
 SAMPLE2
 ... 

## LIMITATIONS
Only limitations of TAXA_REPORT is that you have to use -profile conda. Due to using multiple python libraries in taxa_report.py script you cannot use docker or singularity. I decide to keep going with conda, beacuse it is widely use and wellknown profiler for many users and should not make any troubles for new comming users.

## KRAKEN2 DATABASES
Kraken2 works with databases we can use prepared databases or create our own databases

### PREPARED DATABASE
I highly recommned to use prepared databse called as 'standard', it does contain enough taxons and was created for fast classification, it does only take under 8GB space on your disk. If you think you would benefit more using bigger databse you can download other official databes that kraken2 supports (visit link for more details https://benlangmead.github.io/aws-indexes/k2 ), while using standard databse you do not even have to use parameter --kraken2db path\to\db, because the pipeline deafulty choose standard databse if not specified otherwise. It needs to be said, that prepared databse usually contain data for bacteria, viruses, archaea and human.

### CUSTOM DATABSE
With using command kraken2-build, tool will rpovide you will samll description of possible parameters you can use to build the database.

Must select a task option.
Usage: kraken2-build [task option] [options]

Task options (exactly one must be selected):
  --download-taxonomy        Download NCBI taxonomic information
  --download-library TYPE    Download partial library
                             (TYPE = one of "archaea", "bacteria", "plasmid",
                             "viral", "human", "fungi", "plant", "protozoa",
                             "nr", "nt", "UniVec", "UniVec_Core")
  --special TYPE             Download and build a special database
                             (TYPE = one of "greengenes", "silva", "rdp")
  --add-to-library FILE      Add FILE to library
  --build                    Create DB from library
                             (requires taxonomy d/l'ed and at least one file
                             in library)
  --clean                    Remove unneeded files from a built database
  --standard                 Download and build default database
  --help                     Print this message
  --version                  Print version information

Options:
  --db NAME                  Kraken 2 DB name (mandatory except for
                             --help/--version)
  --threads #                Number of threads (def: 1)
  --kmer-len NUM             K-mer length in bp/aa (build task only;
                             def: 35 nt, 15 aa)
  --minimizer-len NUM        Minimizer length in bp/aa (build task only;
                             def: 31 nt, 12 aa)
  --minimizer-spaces NUM     Number of characters in minimizer that are
                             ignored in comparisons (build task only;
                             def: 7 nt, 0 aa)
  --protein                  Build a protein database for translated search
  --no-masking               Used with --standard/--download-library/
                             --add-to-library to avoid masking low-complexity
                             sequences prior to building; masking requires
                             dustmasker or segmasker to be installed in PATH,
                             which some users might not have.
  --max-db-size NUM          Maximum number of bytes for Kraken 2 hash table;
                             if the estimator determines more would normally be
                             needed, the reference library will be downsampled
                             to fit. (Used with --build/--standard/--special)
  --use-ftp                  Use FTP for downloading instead of RSYNC; used with
                             --download-library/--download-taxonomy/--standard.
  --skip-maps                Avoids downloading accession number to taxid maps,
                             used with --download-taxonomy.
  --load-factor FRAC         Proportion of the hash table to be populated
                             (build task only; def: 0.7, must be
                             between 0 and 1).
  --fast-build               Do not require database to be deterministically
                             built when using multiple threads.  This is faster,
                             but does introduce variability in minimizer/LCA
                             pairs.  Used with --build and --standard options.
                             
First step to create databse is to use command --download-taxony path\to\databse (this is were your new custom database will be created and how it will be names). 
Next process is up to you, at first you can use  
--download-library TYPE --db path\to\database   
                            Download partial library
                             (TYPE = one of "archaea", "bacteria", "plasmid",
                             "viral", "human", "fungi", "plant", "protozoa",
                             "nr", "nt", "UniVec", "UniVec_Core")
Provided partial libraries are pretty huge so be ready to have a lot of free space on your disk.

If you want to add specific specices you can download genomic fasta files (I recommend form NCBI site. because fasta files there have already the right headers that kraken2 requiers). If you have your fasta files ready you cann add them to your library using --add-to-library FILE --db path\to\database

After adding all your fasta files to database you can finally commit last step. Build databse using kraken2-build --build --db path\to\database. After finishing you can clean (delete not more needed files in your database) to free up some space on your disk using kraken2-build --clean --db path\to\database.

## USEFUL SCRIPTS FOR SIMPLIFYING WORK



