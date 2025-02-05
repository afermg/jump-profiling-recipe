

# Run again the profile recipe, since some perturbation was not included in profiles uploaded in cpg  
aws s3 sync --no-sign-request s3://cellpainting-gallery/cpg0014-jump-adipocyte/broad/workspace/backend ~/work/projects/cpg0014-jump-adipocyte/workspace/backend/ --exclude="*" --include="*.csv"

cd ~/work/projects/cpg0014-jump-adipocyte/workspace/software

git clone https://github.com/broadinstitute/${DATA}.git

git submodule add https://github.com/PaulaLlanos/profiling-recipe.git profiling-recipe

https://github.com/cytomining/profiling-recipe.git

# download metadata files

aws s3 sync --no-sign-request s3://cellpainting-gallery/cpg0014-jump-adipocyte/broad/workspace/metadata/platemaps/ metadata/platemaps/

aws s3 sync --no-sign-request s3://cellpainting-gallery/cpg0014-jump-adipocyte/broad/workspace/load_data_csv load_data_csv
gzip -r  load_data_csv


cp profiling-recipe/config_template.yml config_files/config_cpg0014.yml
nano config_files/config_cpg0014.yml

mkdir -p profiles/${BATCH_ID}
find ../../backend/${BATCH_ID}/ -type f -name "*.csv" -exec profiling-recipe/scripts/csv2gz.py {} \;
rsync -arzv --include="*/" --include="*.gz" --exclude "*" ../../backend/${BATCH_ID}/ profiles/${BATCH_ID}/

mkdir -p profiles
find ../backend/ -type f -name "*.csv" -exec profiling-recipe/scripts/csv2gz.py {} \;
rsync -arzv --include="*/" --include="*.gz" --exclude "*" ../backend/ profiles/

python profiling-recipe/profiles/profiling_pipeline.py  --config config_files/config_cpg0014.yml


Primero necesitamos todos los csvs en un solo gran documento, which should include Metadata and Features.
In this big csv we should include also all batches and plates that we want to preprocess:

We need a csv file that contain also this information: 

Source (broad)
Batch
Plate
Well
Perturbation as Metadata_JCP2022, don't change the name of this columns, because we don't want to modify the code downstream

Once we got this, we should conver the csv in parquet files with the function load_Data in the preprocessing folder io.py

this is the first step

also, the metadata_broad_sample column was nan because the broad sample column in the plate map was empty, since it was a control plate. what mean this? there is a empty plate?

Revisar alguno de los archivos de metadata y verifcar que este tenga las columnas que necesitamos.
df=pd.read_csv(f'/home/llanos/2024_10_07_cpg0014_Adipocytes/work/projects/cpg0014-jump-adipocyte/workspace/software/profiles/2022_11_28_Batch2/BR00135823/BR00135823_augmented.csv.gz',compression='gzip')
if df.get('Metadata_Plate') is not None:
    print(f"La columna ''Metadata_Plate'' existe en el DataFrame.")
else:
    print('no metadata_plate column')

activate the environment
------
cd jump-profiling-recipe/
nix develop . --impure --extra-experimental-features nix-command --extra-experimental-features flakes --show-trace


df=pd.read_csv('/home/llanos/2024_10_07_cpg0014_Adipocytes/work/projects/cpg0014-jump-adipocyte/workspace/software/profiles/2022_11_28_Batch1/BR00135656/BR00135656_augmented.csv.gz',compression='gzip')


find names in column name in dataframe
-----
matching_columns = [col for col in df.columns if 'city' in col.lower()]
print(matching_columns)


Source (broad)
Batch
Plate
Well
Perturbation as Metadata_JCP2022,

generating the dataset with cell count
----
Metadata_plate_map_name Metadata_broad_sample Metadata_Plate Metadata_Well  Metadata_Count_Cells

/home/llanos/2024_10_07_cpg0014_Adipocytes/work/get_allmetadata.py


this change is because no all the parquet files has the same feature:

def load_data(sources, plate_types):
    """Load all plates given the params"""
    paths, slices = prealloc_params(sources, plate_types)
    total = slices[-1, 1]

    with pq.ParquetFile(paths[0]) as f:
        meta_cols = find_meta_cols(f.schema.names)
    with pq.ParquetFile(paths[-1]) as f:
        feat_cols = find_feat_cols(f.schema.names)
    meta = np.empty([total, len(meta_cols)], dtype="|S128")
    feats = np.empty([total, len(feat_cols)], dtype=np.float32)


To check phenotipic activity 
---------
    from preprocessing import metrics

    metrics.average_precision_negcon(parquet_path="outputs/orf_public/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet", ap_path="ap_scores.parquet", plate_types=["COMPOUND"])
    metrics.average_precision_negcon(parquet_path="outputs/orf/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet", ap_path="ap_scores.parquet", plate_types=["COMPOUND"])
    metrics.mean_average_precision("ap_scores.parquet", "map_scores.parquet")
    import pandas as pd
    df  = pd.read_parquet("map_scores.parquet")
    df.head(5)
    df.below_corrected_p.value_counts()

pd.read_parquet("outputs/orf/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").Metadata_J
    ...: CP2022.value_counts()
pd.read_parquet("outputs/orf/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").Metadata_p
    ...: ert_type.value_counts()
pd.read_parquet("outputs/orf/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").head()
pd.read_parquet("outputs/orf/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").head().T.h
    ...: ead()
pd.read_parquet("outputs/orf_public/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").hea
    ...: d().T.head()
pd.read_parquet("outputs/orf_public/profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony.parquet").hea
    ...: d().T

MINI-GRANT - NOISE REMOVAL To include noise_removal
-----------

Since this should be done using jump repository, I should clone jump recipe in a new folder, together with the other files that I will need. Once I cloned it, I need to modify some files accordingly:

1- Using the file download_data.sh download jump repository

2-clone jump-profile-recipe

3- in the snakemake file include noise removal, this will give to snakefile a way to connect the input with the output:

rule noise_removal:
    input:
        "outputs/{scenario}/{pipeline}.parquet",
    output:
        "outputs/{scenario}/{pipeline}_noise_removal.parquet",
    run:
        pp.clean.outlier_removal(*input, *output)
    
4- In preprocessing files, in clean.py file. I should i include the noise_removal function.

5- Also in Compund.json, I should include the name of the function in the  steps.

 original: "pipeline": "profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony",
 new version: "pipeline": "profiles_wellpos_cc_var_mad_outlier_noiseremoval_featselect_sphering_harmony",

6- Import the specific dependences to pycytominer folder, in adipocytes i don't import all pycytominer function, I just take a few function, I should take the one that i need in that folder as well. I should add noise_removal function there.

7- run snakemake 



——

orf.json

{
    "scenario": "orf",
    "pipeline": "profiles_wellpos_cc_var_mad_outlier_featselect_sphering_harmony",
    "keep_image_features": false,
    "use_mad_negcon": false,
    "sources": [
        "broad"
    ],
    "plate_types": [
        "COMPOUND"
    ],
    "batch_key": "Metadata_Batch",
    "label_key": "Metadata_JCP2022",
    "sphering_method": "ZCA-cor",
    "sphering_n_opts": 25,
    "cc_path": "inputs/orf_cell_counts_adipocytes.csv.gz"
}

