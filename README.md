# Foodgram 🍴

Foodgram is a web application for sharing recipes and planning grocery shopping.

Users can publish recipes, save their favorite recipes, follow other authors, and generate a shopping list based on selected recipes.

## Features

- User registration and authentication
- Creating, editing, and deleting recipes
- Adding recipes to favorites
- Following other authors
- Adding recipes to a shopping cart
- Downloading a shopping list
- Filtering recipes by tags
- Managing ingredients and tags
- REST API for working with application data
- Admin panel for content management

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Djoser
- PostgreSQL
- Gunicorn

### Infrastructure

- Docker
- Docker Compose
- Nginx
- GitHub Actions

## Project Structure

```text
foodgram/
├── backend/                 # Django REST API
├── frontend/                # Frontend application
├── infra/                   # Infrastructure configuration
├── docs/                    # Project documentation
├── postman_collection/      # Postman API collection
├── .github/workflows/       # CI/CD workflows
├── docker-compose.yml
└── docker-compose.production.yml
```

## Running the Project Locally

Clone the repository:

```bash
git clone https://github.com/P-Kulakova/foodgram.git
cd foodgram
```

Create a `.env` file in the project root and configure the required environment variables.

Example:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

Start the containers:

```bash
docker compose up --build
```

Apply database migrations:

```bash
docker compose exec backend python manage.py migrate
```

Collect static files:

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

Load ingredient data if required:

```bash
docker compose exec backend python manage.py import_csv
```

Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

## API

The project provides a REST API for working with:

- users and authentication;
- recipes;
- ingredients;
- tags;
- subscriptions;
- favorite recipes;
- shopping lists.

API documentation is available in the `docs` directory.

A Postman collection for testing the API is also included in the repository.

## Deployment

The production environment is containerized with Docker Compose and includes:

- PostgreSQL database
- Django backend
- Frontend
- Nginx gateway

The repository also contains a GitHub Actions workflow for automated deployment.

## Author

**Polina Kulakova**

Python Backend Developer

GitHub: [P-Kulakova](https://github.com/P-Kulakova)
