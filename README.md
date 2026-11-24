# FastAPI Calculator – Module 12

## Project Description

This project continues my FastAPI Calculator application from previous modules. In Module 12, I focused on implementing polymorphic relationships, using the Factory Pattern, and validating calculation data with Pydantic.

The application uses FastAPI, SQLAlchemy, and PostgreSQL. It also keeps the secure user management features developed in Module 10.

## GitHub Repository

https://github.com/kevinnbravo9/Module12

## Docker Hub

https://hub.docker.com/r/kevinbravor99/fastapi-calculator-module12

Docker image:

`kevinbravor99/fastapi-calculator-module12:latest`

## Technologies Used

- Python
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy
- Pydantic
- Argon2 password hashing with pwdlib
- Pytest and pytest-cov
- Playwright
- Docker and Docker Compose
- GitHub Actions
- Trivy security scanning
- HTML

## Calculator Features

The calculator supports four basic operations:

- Addition
- Subtraction
- Multiplication
- Division

The application also includes input validation, division-by-zero protection, a web interface, and FastAPI endpoints.

## Module 12 – Polymorphic Calculations

### SQLAlchemy Models

Module 12 introduces a polymorphic calculation model using SQLAlchemy.

The main `Calculation` class represents calculations stored in the database. Four subclasses represent the different operations:

- `Addition`
- `Subtraction`
- `Multiplication`
- `Division`

These subclasses use the same database table and are distinguished by their calculation type.

Each calculation includes an ID, user ID, calculation type (`type`), operands (`a` and `b`), an `inputs` list, an optional result, and creation and update timestamps (`created_at` and `updated_at`).

### Polymorphism

Polymorphism allows the application to work with different calculation types through a common interface.

Each calculation subclass implements its own `get_result()` behavior. This makes it easier to organize the operations and add new calculation types in the future.

### Factory Pattern

The project uses the Factory Pattern through the `Calculation.create()` method.

Instead of manually creating each calculation subclass, the factory selects the appropriate class based on the requested operation.

This reduces repeated code and keeps the calculation creation process organized.

### Pydantic Validation

Pydantic schemas validate calculation data before it is used. `CalculationCreate` accepts either `a`, `b`, and `type`, or the existing `inputs` list and `type`, along with a valid `user_id`. `CalculationRead` includes `a`, `b`, `type`, `result`, and the calculation ID.

The project includes:

- `CalculationType`
- `CalculationBase`
- `CalculationCreate`
- `CalculationRead`
- `CalculationUpdate`
- `CalculationResponse`

Validation checks include:

- Supported calculation types
- At least two input numbers
- Valid numeric values
- Division-by-zero prevention
- Valid user IDs

## Previous Module Features

### PostgreSQL Integration

Module 9 introduced PostgreSQL and database operations, including creating tables, inserting records, updating records, deleting records, and querying data.

### Secure User Management

Module 10 introduced a SQLAlchemy `User` model, Pydantic user schemas, and password hashing.

Passwords are hashed using Argon2 through pwdlib. The user service supports creating users and handling duplicate usernames or email addresses.

The `UserRead` schema excludes password hashes from returned user information.

## Running the Application Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Open the application:

http://localhost:8000

API documentation:

http://localhost:8000/docs

## PostgreSQL and Docker Compose

The project includes a Docker Compose configuration for the application and PostgreSQL environment.

To start the configured services:

```bash
docker compose up -d
```

Make sure the required database settings are configured before running integration tests.

## Automated Testing

The project includes unit, integration, and end-to-end tests.

Run unit tests:

```bash
python -m pytest tests/unit -v
```

Run integration tests:

```bash
python -m pytest tests/integration -v
```

Run end-to-end tests:

```bash
python -m pytest tests/e2e -v
```

Run unit and integration tests together:

```bash
python -m pytest tests/unit tests/integration -q
```

During local Module 12 verification, 71 unit and integration tests passed with 95% overall code coverage.

The integration tests cover calculation operations, polymorphic classes, factory creation, Pydantic validation, division-by-zero protection, the `a` and `b` fields, and database persistence.

## GitHub Actions CI/CD

The GitHub Actions workflow includes three jobs:

1. Test: Runs automated tests, including unit, integration, and end-to-end tests.
2. Security: Builds the Docker image and scans it using Trivy.
3. Deploy: Publishes the Docker image to Docker Hub after the required jobs succeed.

The Module 12 workflow successfully completed all three jobs.

## Docker Hub Deployment

The published Docker image is available at:

https://hub.docker.com/r/kevinbravor99/fastapi-calculator-module12

Pull the image:

```bash
docker pull --platform linux/amd64 kevinbravor99/fastapi-calculator-module12:latest
```

Run the published image:

```bash
docker run -d --name module12_verify --platform linux/amd64 -p 8001:8000 kevinbravor99/fastapi-calculator-module12:latest
```

The published image was downloaded and tested successfully.

The running FastAPI application returned HTTP 200 for:

- `/docs`
- `/openapi.json`

## Conclusion

Module 12 helped me understand how polymorphism and the Factory Pattern can be used with SQLAlchemy models.

I also practiced validating calculation data with Pydantic and writing tests to confirm that the calculations work correctly.

This module builds on the database, security, and CI/CD features developed in the previous assignments.
