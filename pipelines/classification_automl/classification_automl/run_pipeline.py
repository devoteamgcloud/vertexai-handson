"""Run the classification_automl pipeline."""

from google.cloud import aiplatform, bigquery

PROJECT_ID = "workshop-mlops-sandbox"
LOCATION = "europe-west1"
BUCKET_URI = "gs://workshop-mlops-sandbox-classification-automl"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/classification_automl"
PIPELINE_DISPLAY_NAME = "classification-automl"
DATASET_DISPLAY_NAME = "classification-dataset"
MODEL_DISPLAY_NAME = "classification-model"
TRAINING_DISPLAY_NAME = "classification-training-job"
ENDPOINT_DISPLAY_NAME = "classification-endpoint"
MACHINE_TYPE = "n1-standard-4"
BQ_SOURCE = "workshop-mlops-sandbox.ml_datasets.beans1"

client = bigquery.Client()
bq_region = client.get_table(BQ_SOURCE).location.lower()
if bq_region != LOCATION:
    raise ValueError(
        f"BigQuery region {bq_region} does not match pipeline region {LOCATION}"
    )
print(f"Region validated: {LOCATION}")


# Configure the pipeline
aiplatform.PipelineJob(
    project=PROJECT_ID,
    location=LOCATION,
    display_name=PIPELINE_DISPLAY_NAME,
    template_path=(
        f"https://{LOCATION}-kfp.pkg.dev/{PROJECT_ID}/"
        "pipeline-templates/classification-automl/latest"
    ),
    pipeline_root=PIPELINE_ROOT,
    parameter_values={
        "project": PROJECT_ID,
        "gcp_region": LOCATION,
        "bq_source": f"bq://{BQ_SOURCE}",
        "thresholds_dict_str": '{"auRoc": 0.95}',
        "DATASET_DISPLAY_NAME": DATASET_DISPLAY_NAME,
        "TRAINING_DISPLAY_NAME": TRAINING_DISPLAY_NAME,
        "MODEL_DISPLAY_NAME": MODEL_DISPLAY_NAME,
        "ENDPOINT_DISPLAY_NAME": ENDPOINT_DISPLAY_NAME,
        "MACHINE_TYPE": MACHINE_TYPE,
    },
    enable_caching=True,
).submit()
