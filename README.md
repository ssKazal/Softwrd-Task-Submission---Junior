# Vehicle Allocation System

## Installation

Follow these steps to set up and run the project:

> Note: You need to have Docker installed on your machine for it to run successfully.

1. **Setup `.env` file**:

    - Copy the contents of `demo.env` and create a `.env` file in the same directory. Update the `.env` file with your environment-specific settings.

2. **Build the Application**:
    ```sh
    sudo docker compose build
    ```
3. **Up the Application**:
    ```sh
    sudo docker compose up
    ```

## API Documentation

Once the application is running, FastAPI provides two types of interactive API documentation automatically:

1. **Swagger UI**:

    - Accessible at `/docs` (e.g., `http://localhost:8000/docs`).
    - Provides a user-friendly interface to interact with the API.

2. **ReDoc**:
    - Accessible at `/redoc` (e.g., `http://localhost:8000/redoc`).
    - Presents OpenAPI documentation in a more detailed and structured format.

## Testing

1. **To run the tests for the application, use the following command:**
    ```sh
    sudo docker compose run --rm web pytest
    ```
2. **To generate a coverage report, you can use:**
    ```sh
    sudo docker compose run --rm web pytest --cov=src
    ```

## Deployment

When deploying the application, consider using a VPS (Virtual Private Server) or cloud service (e.g., AWS) with root access to a Linux system.

1. **Modify Caddyfile**:

    - Update the `Caddyfile` with your domain and any necessary configurations.

2. **Deploy the Application**
    ```sh
    sudo docker compose -f docker-compose-prod.yml build
    sudo docker compose -f docker-compose-prod.yml up -d
    ```
