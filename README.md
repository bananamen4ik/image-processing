# Image Processing Service

A Django-based web service for processing images.

## Overview

This project is a portfolio web application built with Django.

Users can upload images, select processing operations, and receive the processed result.

## Run All Tests

Runs a complex tests of the entire project.

`pre-commit run && pre-commit run --hook-stage=manual`

### Running Tests Individually

Runs tests one at a time.

#### Coverage

`pre-commit run --hook-stage=manual coverage`

#### Ruff Check

`pre-commit run ruff-check`

#### Ruff Format

`pre-commit run ruff-format`

#### Ty

`pre-commit run ty`