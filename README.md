# Instructions to setup and run the project
- Create a virtual environment for python

  `python -m venv .venv`

  `source .venv/bin/activate`
- Install all the requirements

  `pip install -r requirements.txt`

- create a .env file at the root of the directory  (example shown in `.env.example`)

  `touch .env`

- Add the following env variable for the postgresql database

  `SQLALCHEMY_DATABASE_URL=[username]://[password]:[server_name]@localhost:5432/[db_name]`

- run the `main.py` file

  `uvicorn app.main:app --reload`
