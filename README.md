# Remi — Dog Activity Tracking & Prediction

Remi is a software project focused on tracking dog activity and exploring behavior prediction using machine learning.

The project combines a backend API, database integration, and a frontend application.

## Features

- REST API built with FastAPI
- PostgreSQL database integration
- SQLAlchemy for database operations
- JWT-based authentication
- Machine learning model for prediction
- Docker Compose for running the project services

## Tech Stack

| Category | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Machine Learning | scikit-learn, Random Forest |
| Development Tools | Docker, Docker Compose |

## Project Structure

```text
remi/
├── backend/
├── frontend/
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Git
- Docker and Docker Compose

### Installation

Clone the repository:

```bash
git clone https://github.com/jagudes/remi.git
cd remi
```

Start the services using Docker Compose:

```bash
docker compose up --build
```

**Note:** Additional environment variables or configuration may be required. Check the project configuration before running the application.

## Project Goals

This project provides practical experience with backend development, database integration, API design, containerization, and machine learning.

## Author

**Jagoda Jamróz**

GitHub: [@jagudes](https://github.com/jagudes)
