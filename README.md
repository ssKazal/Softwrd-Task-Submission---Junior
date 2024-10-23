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

## Deployment

1. **Modify Caddyfile**:

    - Update the `Caddyfile` with your domain and any necessary configurations.

2. **Deploy the Application**
    ```sh
    sudo docker compose build
    sudo docker compose up -d
    ```
