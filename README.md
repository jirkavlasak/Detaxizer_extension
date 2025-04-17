# Detaxizer_extension
## Welcome to my own Detaxizer extension
This project is based on my bachelor thesis, where my goal was to find sufficent nf-core based pipeline, which is possible to edit and implement new porcesses, specially to find contaminations in sequacing data adn create HTML page report about sample.
All files you can find here are not part of the original Detaxizer pipeline, but will help you to implement my process to pipeline and I will provide here to you a little guid how to do so.
But first, please be sure your Detaxize pipeline is installed correctly.

## ABOUT
### YOU CAN MODIFY taxa_report.py to meet your criteria
Main focus here is on taxa_report.py and taxa_report.nf. These scripts are new additional process for Detaxizer pipeline. Script take input from kraken2 classification report and original name of sample given in sample sheet. Scripts return phylogenetic tree of classifed taxons in kraken2 classification report and HTML report page with summary of that classification. Note that taxa_report.py filters lines where taxons had zero values at classification, sorts lines by percentage values and trimms taxons that their classification value was to loo to considre tham as rightfully classifed and are most likley some kind of buzz. 


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

## LIMITATIONS
Only limitations of TAXA_REPORT is that you have to use -profile conda. Due to using multiple python libraries in taxa_report.py script you cannot use docker or singularity. I decide to keep with conda, beacuse it is widely use and well known profile for many users and should not make any troubles for new comming users.

## LAUCHING PIPELINE

## LAUCHING PIPELINE WITH MULTIPLE SAMPLES

## KRAKEN2 DATABASES

