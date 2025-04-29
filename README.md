# Vertex AI Hands-On

## Problem 1 (1h): Classification AutoML

### Problem statement

The objective of this hands-on exercise is to train, evaluate, and understand a classification model using Vertex AI AutoML tabular models. You will work with a public dataset containing information about different types of beans, stored in BigQuery (aju-dev-demos:beans.beans1).

The entire workflow, from setting up the necessary Google Cloud infrastructure (APIs, permissions, Artifact Registry, GCS bucket, BigQuery dataset) to orchestrating the AutoML training job, will be managed using a Vertex AI Pipeline. You will define this pipeline, compile it, store the compiled template in Artifact Registry, and finally execute the pipeline run on Vertex AI. The goal is to successfully run the pipeline which trains an AutoML classification model on the provided bean dataset.

### Challenge

Read the code in `pipelines/classification_automl/classification_automl/pipeline.py` and fill in the blanks. Do not run any code yet.
The following documentation may help you in your task: [https://cloud.google.com/vertex-ai/docs/pipelines/gcpc-list](https://cloud.google.com/vertex-ai/docs/pipelines/gcpc-list).

Once done, read the code in `pipelines/classification_automl/classification_automl/components/evaluation.py` and make sure you understand it thoroughly.

Finally, pause there, call one of the instructors and be ready to answer the following questions (hint: remember the enablement sessions):

- What is MLOps and why is it important?
- What stages of MLOps are we missing in this implementation?
- How would you incorporate data from a different warehouse?

### Instructions

1) Go to Artifact Registry and activate the API
2) Go to Vertex AI and activate the API
3) Enable the Compute Engine API
4) Grant yourself the Service Account Token Creator role
5) Once done, go to Artifact Registry and create a repository named `pipeline-templates` with type `Kubeflow pipelines`
6) Build the pipeline by running the following command (after having changed the necessary variables):

``` bash
_PROJECT_ID="workshop-mlops-sandbox"
_REGION="europe-west1"
_ARTIFACT_REGISTRY_TEMPLATES_URL="https://${_REGION}-kfp.pkg.dev/${_PROJECT_ID}/pipeline-templates"

uv run classification_automl/pipeline.py \
    --project ${_PROJECT_ID} \
    --region ${_REGION} \
    --pipeline-name classification-automl \
    --pipeline-file classification-automl.yaml \
    --artifact-registry-url ${_ARTIFACT_REGISTRY_TEMPLATES_URL} \
    -t latest
```

7) Create a multi-region bucket (EU) named "{PROJECT_ID}-classification-automl"
8) Create a BQ dataset in EU:

``` bash
bq mk --location=EU --dataset {PROJECT_ID}:ml_datasets
```

9) Copy the example table in your newly created dataset:

``` bash
bq cp aju-dev-demos:beans.beans1 {PROJECT_ID}:ml_datasets.beans1
```

10) Adapt the variables in `classification_automl/run_pipeline.py` and run the pipeline by launching the following command:

``` bash
uv run classification_automl/run_pipeline.py
```

## Problem 2 (30 mins): Classification BigQuery ML

### Problem statement

This exercise shifts focus from Vertex AI AutoML Pipelines to BigQuery ML (BQML). The objective is to train a classification model directly within BigQuery using SQL syntax, leveraging the same bean dataset used in Problem 1. This approach highlights the power of performing machine learning tasks directly where your data resides in the data warehouse.

You will use the `beans1` table previously copied into your `ml_datasets` BigQuery dataset (`{PROJECT_ID}:ml_datasets.beans1`). Your goal is to write and execute a CREATE MODEL statement in BigQuery to train a model that predicts the bean Class (the target variable), similar to the task performed by the AutoML model in Problem 1. You will explore the simplicity of in-warehouse model training and compare this workflow to the pipeline-orchestrated approach of Vertex AI.

### Challenge

1. Write a BigQuery SQL query using the `CREATE OR REPLACE MODEL` statement.
2. Configure the model:

- Specify an appropriate MODEL_TYPE for classification (e.g., LOGISTIC_REG, BOOSTED_TREE_CLASSIFIER, or even AUTOML_CLASSIFIER to compare AutoML implementations).
- Define the INPUT_LABEL_COLS to be the target variable ('Class').
- Ensure all other relevant columns from the beans1 table are used as input features in the SELECT statement defining the training data.

3. Execute the query successfully in the BigQuery console or using the bq command-line tool to train the model.
4. (Optional but recommended) After training, use the ML.EVALUATE function to assess the performance of your BQML model.
5. (Optional but recommended) Use ML.PREDICT to make predictions on a sample of the data.
6. Reflect: Consider the differences in development experience, infrastructure setup, control over the training process, and overall workflow compared to the Vertex AI AutoML Pipeline approach in Problem 1.

## Problem 3 (2h30): Create your own custom model

### Problem statement

Now that you've experienced the managed approach of Vertex AI AutoML (Problem 1) and the SQL-centric BigQuery ML (Problem 2), this exercise dives into building a Vertex AI Pipeline for a custom model. You will train, evaluate, and potentially register a Scikit-learn classifier on the same bean dataset.

This approach gives you maximum flexibility and control over your model architecture, training process, and dependencies, but requires more explicit MLOps steps like packaging your code and managing training environments. You will leverage Vertex AI Pipelines to orchestrate the workflow, including data preparation, custom training using a container, and model evaluation. The goal is to build and run a pipeline that successfully trains your own sklearn model on Vertex AI infrastructure.

### Challenge

- Data Preparation: Define a pipeline component (or use a pre-built one like `google_cloud_pipeline_components.v1.bigquery.BigqueryQueryJobOp`) to execute a query against the `beans1` table in BigQuery (`{PROJECT_ID}:ml_datasets.beans1`) and export the data (features and target) to a CSV file in a GCS bucket.
- Training Script: Create a Python script (`train.py`) that:
  - Accepts the GCS path to the training data CSV as an argument.
  - Loads the data (e.g., using pandas).
  - Performs any necessary simple preprocessing (e.g., handling categorical features if needed, splitting data - though Vertex custom jobs can inject data splits).
  - Instantiates and trains a Scikit-learn classifier (e.g., RandomForestClassifier, LogisticRegression).
  - Saves the trained model artifact (e.g., using `joblib.dump`) to the GCS location specified by the AIP_MODEL_DIR environment variable (Vertex AI Training automatically sets this up for model output).
- Containerization:
  - Create a Dockerfile that starts from a Python base image (e.g., `python:3.9`), copies your `train.py` script, and installs necessary dependencies (google-cloud-aiplatform, scikit-learn, pandas, gcsfs, joblib, etc.) listed in a requirements.txt file.
  - Build the Docker image.
  - Push the image to your Artifact Registry repository (you might need to create a new repo with Docker format or use an existing one).
- Pipeline Definition: Create a new pipeline definition file (e.g., `sklearn_pipeline.py`) using the KFP SDK:
  - Define the data preparation step.
  - Use the `google_cloud_pipeline_components.v1.custom_job.CustomTrainingJobOp` component to run your training script:
    - Configure it to use the custom container image URI from Artifact Registry.
    - Pass the GCS path of the prepared data CSV as an argument to your script.
    - Specify necessary resources (machine type, e.g., `n1-standard-4`).
    - Define the expected output model artifact location.
  - Define an evaluation component: This will likely be another custom component (similar structure: script, Dockerfile, CustomTrainingJobOp or potentially a lighter `kfp.dsl.component` if dependencies are simple) that:
    - Takes the trained model artifact GCS URI (output from the training step) and test data (can be from the same exported CSV or a dedicated split) as input.
    - Loads the model and data.
    - Calculates evaluation metrics (e.g., accuracy).
    - Outputs the metrics.
- Compile and Run: Compile your pipeline and submit the run to Vertex AI Pipelines.
- Verify: Monitor the pipeline run. Check the logs for each component, especially the custom training job. Verify that the model artifact is created in GCS and that the evaluation metrics are produced.
- (Optional) Model Registration: Add a `ModelUploadOp` step after successful training/evaluation to register your custom sklearn model. This requires specifying:
  - The GCS URI of the saved model artifact.
  - A serving container image URI. You can use a Vertex AI pre-built sklearn container or build your own serving container (more advanced).

### Instructions & Hints

- Data Export: `BigqueryQueryJobOp` can execute a query. To export, you might need to query into a temporary BQ table and then use `BigqueryExportJobOp`, or write a small custom component using the BigQuery client library to run `extract_table`. Alternatively, query within your training script using `pandas.read_gbq`.
- Training Script Args: Use argparse in `train.py` to receive the data path.
- Model Saving: Save the model to `$AIP_MODEL_DIR/model.joblib`. Vertex AI uses this environment variable convention.
- Dockerfile: Keep it simple. Start `FROM python:3.9`, set `WORKDIR /app`, `COPY requirements.txt` and `train.py`, `RUN pip install -r requirements.txt --no-cache-dir`, define `ENTRYPOINT ["python", "train.py"]`.
- Building/Pushing Image: Use `docker build -t <IMAGE_URI> .` and `docker push <IMAGE_URI>`. The `<IMAGE_URI>` should be like `{REGION}-docker.pkg.dev/{PROJECT_ID}/{ARTIFACT_REGISTRY_REPO_NAME}/sklearn-trainer:latest`. Ensure Artifact Registry API is enabled and you have permissions (`gcloud auth configure-docker {REGION}-docker.pkg.dev`). (Hint: take inspiration from [here](https://github.com/GoogleCloudPlatform/vertex-pipelines-end-to-end-samples/blob/main/pipelines/src/pipelines/tensorflow/training/assets/train_tf_model.py))
- `CustomTrainingJobOp`:
  - `display_name`: Name for the training job.
  - `worker_pool_specs`: List containing a dictionary defining machine type, replica count, and crucially the container_spec (with image_uri and args for your script).
  - `base_output_directory`: GCS path where outputs (like the model) will be placed relative to the `AIP_MODEL_DIR`.
- Evaluation Component: Structure similarly to the training component. It needs inputs for the model URI (from the training step's output) and data URI. It should load the model using `joblib.load` and output metrics (e.g., using print() for logs, or writing to output_metadata).
- Permissions: The Vertex AI service account needs roles/permissions for BigQuery (read), GCS (read/write), Vertex AI Training Jobs (create), Artifact Registry (read), and potentially Vertex AI Model Registry (upload).
- (Optional) Pre-built Containers: Vertex AI offers pre-built containers for training and serving standard frameworks like sklearn. Using a pre-built training container can sometimes simplify the `CustomTrainingJobOp` configuration as you don't always need a custom Dockerfile, just your script. Check the Vertex AI documentation for compatibility. For serving (in `ModelUploadOp`), using a pre-built sklearn serving container is often the easiest path.
