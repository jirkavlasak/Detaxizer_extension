import os
import shutil



source_dir = "/home/jirka_vlasak/detaxizer_pipeline/input_fastq"
samples_dir = "/home/jirka_vlasak/detaxizer_pipeline/SAMPLESDIR"


os.makedirs(samples_dir, exist_ok=True)


for filename in os.listdir(source_dir):
    if filename.endswith(".fastq.gz"):
        sample_name = filename.replace(".fastq.gz", "")

        
        sample_path = os.path.join(samples_dir, sample_name)
        workdir = os.path.join(sample_path, "workdir")
        outdir = os.path.join(sample_path, "outdir")
        
        os.makedirs(workdir, exist_ok=True)
        os.makedirs(outdir, exist_ok=True)
        

print("Done: ", samples_dir)
