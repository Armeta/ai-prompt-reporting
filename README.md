# Nurse AI

This internal project utilizes AI to match nurses to requisitions for nurse staffing companies.

## Getting Started

These instructions should get you set up to work on the streamlit app.

### Prerequisites

* Python 3.10
* pip

### Installation

After cloning the repo, open a CLI to follow along.

```
$ cd path/to/ai-prompt-reporting/directory
$ python -m venv .venv
$ .\.venv\Scripts\Activate.ps1
$ pip install -r requirements.txt
```

### Setup
After pip is done installing the packages, you must create the `secrets.toml` file in the
`.streamlit` directory. This file includes the necessary credentials to establish a connection
to Armeta's Snowflake instance. Fill in the `user` and `password` fields.

```
account = "kv21351-zs31584"
user = "<username>"
password = "<password>"
role = "ARMETA_AI_ROLE"
warehouse = "ARMETA_AI_WH"
database = "ARMETA_AI"
schema = "NURSE"
```


## Usage

Run the following command in a CLI to launch the streamlit app in a web browser.

```
$ streamlit run streamlit_app.py
```
