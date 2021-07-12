# BACKEND

The Backend part provides the API which will be used with the frontend later and will provide it with the required functionalities, including the ones specified in the project description and the ones we did in the labs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the libraries found in the requirements.txt files, which will be needed to run the frontend (in addition to a running version of python). We do so by running the following command after activating the virtual environment:



```bash
pip install -r requirements.txt
```

Note, after installing requirements, you may need to do the following :
pip uninstall JWT, then pip uninstall PyJWT, then finally pip install PyJWT
since there is a name conflict between the two packages which affects the import

## Usage

After the required libraries are installed and we have the backend documents on our system, we will need to run our backend locally using the following:
```bash
FLASK_APP=app.py FLASK_ENV=development flask run
```

Note, you will need to have a MYSQL server running locally, and change the root to your password. You must also create a new schema named exchange, and use the following script:
```
from app import db
db.create_all()
```
to initialize the database

## Documentation

You can find the documentation of the backend API layer using the openAPI specification on the following link: https://app.swaggerhub.com/apis/srz08/exchange-backend/1.0.0 
