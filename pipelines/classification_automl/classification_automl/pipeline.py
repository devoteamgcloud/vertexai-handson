"""Pipeline definition for ragas generation."""
# pylint: disable=duplicate-code,too-many-arguments,too-many-locals,too-many-positional-arguments

import argparse

from components.evaluation import classification_model_eval_metrics
from google_cloud_pipeline_components.v1.automl.training_job import (
    AutoMLTabularTrainingJobRunOp,
)

# pylint: disable=line-too-long
from google_cloud_pipeline_components.v1.dataset.create_tabular_dataset.component import (  # noqa: E501
    tabular_dataset_create as TabularDatasetCreateOp,
)

# pylint: enable=line-too-long
from google_cloud_pipeline_components.v1.endpoint.create_endpoint.component import (
    endpoint_create as EndpointCreateOp,
)
from google_cloud_pipeline_components.v1.endpoint.deploy_model.component import (
    model_deploy as ModelDeployOp,
)
from kfp import compiler, dsl
from kfp.registry import RegistryClient

parser = argparse.ArgumentParser()
parser.add_argument(
    "--project",
    help="the project ID",
    type=str,
)
parser.add_argument(
    "--region",
    help="the region where the pipeline will be stored",
    type=str,
)
parser.add_argument(
    "--pipeline-name",
    help="the name of the pipeline",
    type=str,
    default="scrape",
)
parser.add_argument(
    "--pipeline-file",
    help="the location to write the pipeline JSON to",
    type=str,
    default="pipeline.yaml",
)
parser.add_argument(
    "--artifact-registry-url",
    help="the Artifact Registry URL to save the pipeline template to",
    type=str,
)
parser.add_argument(
    "-t",
    "--tags",
    nargs="*",
    help="Extra tags to set on the image.",
    default=["latest"],
)
args = parser.parse_args()


@dsl.pipeline(name=args.pipeline_name)
def pipeline(
    bq_source: str,
    DATASET_DISPLAY_NAME: str,
    TRAINING_DISPLAY_NAME: str,
    MODEL_DISPLAY_NAME: str,
    ENDPOINT_DISPLAY_NAME: str,
    MACHINE_TYPE: str,
    project: str,
    gcp_region: str,
    thresholds_dict_str: str,
) -> None:
    """Vertex AI pipeline setup."""
    dataset_create_op = TabularDatasetCreateOp(
        project=project,
        location=gcp_region,
        display_name=DATASET_DISPLAY_NAME,
        bq_source=bq_source,
    )

    training_op = AutoMLTabularTrainingJobRunOp(
        project=project,
        location=gcp_region,
        display_name=TRAINING_DISPLAY_NAME,
        optimization_prediction_type=...,  # TODO
        optimization_objective=...,  # TODO
        budget_milli_node_hours=1000,
        model_display_name=MODEL_DISPLAY_NAME,
        column_specs=...,  # TODO
        dataset=...,  # TODO
        target_column=...,  # TODO
    )

    model_eval_task = classification_model_eval_metrics(
        ...  # TODO
    )

    with dsl.If(
        model_eval_task.outputs["dep_decision"] == "true",
        name="deploy_decision",
    ):
        endpoint_op = EndpointCreateOp(
            project=project,
            location=gcp_region,
            display_name=ENDPOINT_DISPLAY_NAME,
        )

        ModelDeployOp(
            model=training_op.outputs["model"],
            endpoint=endpoint_op.outputs["endpoint"],
            dedicated_resources_min_replica_count=1,
            dedicated_resources_max_replica_count=1,
            dedicated_resources_machine_type=MACHINE_TYPE,
        )


compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path=args.pipeline_file,
)

client = RegistryClient(host=args.artifact_registry_url)
templateName, versionName = client.upload_pipeline(
    file_name=args.pipeline_file,
    tags=args.tags,
)
