# Detaxizer_extension
This project is based on my bachelor thesis, the goal being finding a sufficent nf-core based pipeline, in which it is possible to edit and implement new processes, specifically to find contaminations in sequacing data and to create a HTML page report about sample. All of the files found here are not part of the original Detaxizer pipeline, but will help you to implement the new processes to the pipeline. A guide on how to implement the new processes is also provided here. But first, please be sure your Detaxizer pipeline is installed correctly. Link to official site of Detaxizer pipeline: https://nf-co.re/detaxizer/1.0.0/

## ABOUT
### You can modify taxa_report.py to meet your criteria
The main focus here is on taxa_report.py and taxa_report.nf. These scripts are new additional processes for Detaxizer pipeline. The script takes input from kraken2 classification report and the original name of the sample given in the sample sheet. Scripts return a phylogenetic tree of classifed taxons in a kraken2 classification report and a HTML report page with a summary of that classification. Note that taxa_report.py filters out lines where taxons had values equal to zero at classification, sorts lines by percentage values and trims taxons which had their classification value too low to consider them as rightfully classified and are most likely some kind of buzz.
<p align="center">
  <img src="https://github.com/user-attachments/assets/16ae2d6b-abde-4fb2-909c-6c3010def4e3" alt="Popis obrázku" width="300"/>
</p>



## CONFIGURATION
After downloading and installing Detaxizer pipeline, you should look at the configuration settings, the default settings require that your machine has at least 32GB RAM and 8CPUs ready. If you cannot meet these requirements on your machine or you just want to go with a different configuration, you can either create your own or use mine (found in repository named as 'custom.config'). After creating a configuration, you'll have add a "-c" parameter while launching pipeline. For example if I run pipeline with my custom.config file I add to command .... -c path\to\custom.config

## IMPLEMNTING TAXA REPORT 
To add a Taxa report to the Detaxizer pipeline, first you should add taxa_report.py to the ~\detaxizer\bin folder and then continue by adding taxa_report.nf to the  ~\detaxizer\modules\local folder. The next step is to include the newly created module into ~detaxier\workflows\detaxier.nf as include { TAXA_REPORT } from '../modules/local/taxa_report'. After all that you have to add the process itself. I recommend putting TAXA_REPORT process right before the SUMMARY_CLASIFICATION process to keep the analytic and summary part separated, but it is up to you, note that there is a limitation to where you can put it, you have to place the TAXA_REPORT process  below the KRAKEN2_KRANE2 process, because TAXA_REPORT requires the input that is made by KRAKEN2_KRAKEN2 

### TAXA_REPORT PROCESS
Below is an example of a  process to be added as described earlier in IMPLEMETING TAXA REPORT 

    TAXA_REPORT(
        KRAKEN2_KRAKEN2.out.report.map { meta, path ->
               return [meta, path, meta.id] 
                            }
        )
        ch_versions = ch_versions.mix(TAXA_REPORT.out.versions.first())
        ch_taxa_tree = TAXA_REPORT.out.tree_image
        ch_taxa_html = TAXA_REPORT.out.html_report

## WORK ENVIRONMENT
I recommend keeping all samples, sample sheets, workdir and outdir in the same directory for better manipulation. For example I obtained 24 human samples and one mouse sample. For each sample I created folder named as the sample. Inside that folder I kept sample data, workdir and outdir. Below is simple schema for better visualization.


MAIN_FOLDER\
-SAMPLE1\
--sample.fastq.gz\
--WORKDIR\
--OUTDIR\
-SAMPLE2\
 ... 

## LIMITATIONS
The only limitation of TAXA_REPORT is that you have to use -profile conda. Due to using multiple python libraries in taxa_report.py script you cannot use docker or singularity. I decided to stick with conda, because it is a widely used and well known profiler for many users and should not cause any problems for newcoming users.

## KRAKEN2 DATABASES
he databases Kraken2 works with can either be prepared databases or our own user created databases


### PREPARED DATABASE
 highly recommend using a prepared database referred to as 'standard', it contains enough taxons and was created for fast classifications, and it takes less than 8GB of space on your disk. If you think you would benefit from using a bigger database you can download another official database that kraken2 supports (visit link for more details https://benlangmead.github.io/aws-indexes/k2 ), while using the standard database you do not have to use the parameter --kraken2db path\to\db, since the pipeline chooses the standard database by default. It needs to be noted, that the prepared databases usually contain data for bacteria, viruses, archae and humans.

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
Sricpts are easy to implement and do not require more explanation

### DOWNLOAD FASTA FILES FOR CUSTOM DATABASE
If you decided to build your own custom database, I recommend to use this scirpt 'downlaod_fenmos.sh', it get fasta files for specific TAXON ID form NCBI genom data sets. You have to change list of TAXON IDs to get your wanted taxons.Image below shows what you should change to obtain your wanted fasta files. Input parameter is path to the folder you want to store fasta files.
<p align="center">
  <img src="https://github.com/user-attachments/assets/376e1fb8-c89d-47f3-b6f0-c0a178c38c84" alt="Popis obrázku" width="300"/>
</p>


