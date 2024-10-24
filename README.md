# CompanionBot 3000


## Prerequisites

- **Conda**: Ensure you have [Anaconda](https://www.anaconda.com/products/distribution) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.
- Python 3.10 (the environment is set up for Python 3.10).

## Repository

You can clone the repository from:

```bash
git clone git@github.com:Adanato/CompanionBot3000.git
cd CompanionBot3000/backend

```

## Setting Up the Environment
Step 1: Create and Activate Conda Environment
If you haven't already created the Conda environment named CS_4804, do so with the following steps. If the environment already exists, you can skip the creation and just activate it.


## Create the environment if it doesn't exist
```bash
conda create --name CS_4804 python=3.10
```

## Activate the environment
```bash
conda activate CS_4804
```

Step 2: Install Required Python Packages
With the environment active, navigate to the backend folder of the project and install the necessary dependencies for Flask, SocketIO, and CORS.

```bash
pip install Flask Flask-SocketIO Flask-CORS
```

## Run server
```bash
python app.py
```
