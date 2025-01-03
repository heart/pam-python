# pam-python

**pam-python** is a framework designed to simplify the creation of data plugins for PAM Real CDP. These data plugins allow you to extend the capabilities of PAM CDP to process data in a fully customizable way. For example, you can create RFM segments, run analytics such as finding top spenders, and more.

## Features

- Streamlined creation of data plugins for PAM Real CDP.
- Scaffolding for project and service structures.
- Built-in templates for rapid development.
- Command-line utility for managing projects and services.
- Easy-to-run testing for individual services.

## Getting Started

### Prerequisites

- Python 3.6 or later
- pip for package management

## Installation

### 1. Create a new folder for your project

```bash
mkdir my_data_plugin
cd my_data_plugin
```

### 2. Set up a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install pam-python

```bash
pip install pam-python
```

> Once installed, the `pam` command-line utility will be available.

## Usage

### 1. Initialize a New Project

To initialize a new data plugin project, run:

```bash
pam init
```

> This command will create the necessary files and structure for your project.

### 2. Add a New Service

Within your project, you can create multiple services. To add a new service, use:

```bash
pam new service <service_name>
```

> This will create a folder named `<service_name>` containing the following:
> Basic template files to help you start developing your service.

### 3. Test a Service

To test a specific service, use:

```bash
pam test <service_name>
```

> This command will automatically run all test files (\*.test.py) associated with the specified service.

---

## Example Workflow

### 1. Initialize the project

```bash
pam init
```

### 2. Create a new service

```bash
pam new service RFMAnalysis
```

### 3.Customize the service by editing the generated templates in RFMAnalysis

### 4. Test the service

```bash
pam test RFMAnalysis
```
