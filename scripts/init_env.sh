#!/bin/bash

# Pipelines
echo "Syncing pipelines..."
echo "- pipelines/classification_automl"
(cd pipelines/classification_automl && uv sync --all-groups)
