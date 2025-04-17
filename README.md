# Detaxizer_extension
## Welcome to my own Detaxizer extension
This project is based on my bachelor thesis, where my goal was to find sufficent nf-core based pipeline, which is possible to edit and implement new porcesses, specially to find contaminations in sequacing data adn create HTML page report about sample.
All files you can find here are not part of the original Detaxizer pipeline, but will help you to implement my process to pipeline and I will provide here to you a little guid how to do so.
But first, please be sure your Detaxize pipeline is installed correctly.

## SET UP
If you managed to download and install Detaxizer pipeline, you should firstly look at configuration settings, it is set by default that you gotta have at least 36GB RAM and 8CPUs ready for the run. If you do not have these technological parameters on your machine or you just do not want to go withis this configuration, you can create or use mine (you can find it in repository named as 'custom.config'). After creating this configurations, you have add -c parameter while laucnhing pipeline. For example if I run pipeline with my custom.config file I add to command  .... -c path\to\custom.config
