# Educational Center Management System

Course project developed with Django REST Framework and PostgreSQL.

## Overview

Educational Center Management System is a web application for managing educational centers with multiple branches.

The system allows administrators and teachers to manage:

* Branches
* Subjects
* Students
* Groups
* Subscription plans
* Lesson scheduling
* Attendance tracking
* Reports

## Technologies

### Backend

* Python 3.12
* Django
* Django REST Framework
* JWT Authentication
* PostgreSQL
* drf-spectacular (Swagger/OpenAPI)

### DevOps

* Docker
* Docker Compose

## User Roles

### Administrator

Can:

* Manage branches
* Manage subjects
* Manage students
* Manage groups
* Manage subscription plans
* Create lesson schedules
* Create lesson templates
* View reports
* Manage attendance

### Teacher

Can:

* View own schedule
* View students of own lessons
* Mark attendance
* View lesson information

## Installation

### Clone repository

```bash
git clone <repository-url>
cd EduProject
```

### Environment Variables

Create `.env` file in the project root:

```env
DEBUG=True

POSTGRES_DB=education_center
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

SECRET_KEY=your-secret-key
```

## Running with Docker

Build and start containers:

```bash
docker compose up --build
```

Run in background:

```bash
docker compose up -d --build
```

## Database Migration

```bash
docker compose exec backend python manage.py migrate
```

## Create Superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

## Run Tests

```bash
docker compose exec backend python manage.py test
```

## API Documentation

Swagger UI:

```text
http://localhost:8000/api/schema/swagger-ui/
```

OpenAPI Schema:

```text
http://localhost:8000/api/schema/
```

## Main Features

### Authentication

* Phone number authentication
* JWT access token
* JWT refresh token
* Role-based permissions

### Branch Management

* Create branches
* Archive branches
* Branch-based data isolation

### Student Management

* Student registration
* Parent/guardian information
* Student archiving
* Search and filtering

### Group Management

* Create groups
* Add/remove students
* Historical membership tracking

### Subscription Plans

* Pricing grids
* Subject-specific plans
* Student subscriptions

### Lesson Scheduling

* Individual lessons
* Group lessons
* Recurring lesson templates
* Conflict detection

### Attendance

* Present/Absent tracking
* Teacher notes
* Attendance history

### Reporting

* Teacher schedules
* Student attendance history
* Branch statistics

## Business Rules Implemented

### Conflict Detection

The system prevents:

* Teacher schedule conflicts
* Student schedule conflicts

Overlap rule:

```text
start_1 < end_2
AND
start_2 < end_1
```

Cancelled lessons are ignored during conflict checking.

### Permissions

Teachers can access only:

* Their own lessons
* Their own students
* Their own attendance records

Administrators have full access within assigned branches.

## Project Structure

```text
EduProject/
│
├── users/
├── branches/
├── students/
├── groups/
├── subjects/
├── lessons/
├── attendance/
├── subscriptions/
│
├── config/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Testing Coverage

Tests include:

* User model
* Authentication
* Lesson conflict detection
* Attendance creation/update
* API permissions
* Core business logic

## Author

Course Project

Educational Center Management System