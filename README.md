# Image Processing Service

A Django-based web service for processing images.

## Overview

This project is a portfolio web application built with Django.

Users can upload images, select processing operations, and receive the processed result.

## Running Tests

Run the following commands from the project root directory:

1. `cd src/image-processing`.
2. `coverage run --rcfile="../../pyproject.toml"`.
3. `coverage report -m --skip-covered`.

## Running Ruff

Run the following commands from the project root directory:

1. `cd src/image-processing`.
2. `ruff check --config="../../pyproject.toml" --fix`.
3. `ruff format --config="../../pyproject.toml"`.