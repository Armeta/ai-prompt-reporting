# Price Chopper AI

This internal project utilizes AI to provide answers to grocery retail data questions.

## Usage

### Launching

Run the following command in a CLI to launch the streamlit app in a web browser. Give the chat AI prompts to see the options returned.

```
$ streamlit run streamlit_app.py
```

### Creating Options

Use `BuildOptions.py` to provide answer options that the AI can respond with.
Define parameterized answer templates in `src\json\AllTemplates.json`
Run `BuildOptions.py` to parse the templates, and generate option records.


## Local App Setup

### Local Installation

Insure Python 3.9 and pip are installed.
Clone the repo, and run the following command to install necessary python packages.

```
$ pip install -r requirements.txt
```

### Crediential Setup
You must create or update the `.streamlit/secrets.toml` file. This file includes the necessary credentials to establish a connection
to Armeta's Snowflake instance. Fill in the `user` and `password` fields.

```
account = "kv21351-zs31584"
user = "<username>"
password = "<password>"
role = "ARMETA_AI_ROLE"
warehouse = "ARMETA_AI_WH"
database = "ARMETA_AI"
schema = "PC"
```

