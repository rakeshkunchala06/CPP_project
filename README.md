# TransitAccess - Accessible Public Transit Trip Planner

Cloud Platform Programming - National College of Ireland

## Student Information
- **Student:** Rakesh Kunchala
- **Module:** Cloud Platform Programming
- **Repository:** [rakeshkunchala06/CPP_project](https://github.com/rakeshkunchala06/CPP_project)

## Project Overview

A cloud-native accessible public transit trip planner that helps people with mobility needs plan transit trips with accessibility information. Users can search routes, filter by accessibility features (wheelchair ramps, elevators, tactile paving, etc.), view schedules, and save favorite routes.

## AWS Services (6)

| Service | Purpose | Resource Name |
|---------|---------|---------------|
| AWS Lambda | Backend API | transitaccess-api |
| Amazon DynamoDB | Database | transitaccess-prod |
| Amazon API Gateway | REST API | transitaccess-api |
| Amazon S3 | File storage + frontend hosting | transitaccess-files-prod-rakesh / transitaccess-frontend-prod-rakesh |
| Amazon SNS | Email notifications | transitaccess-notifications |
| AWS IAM | Role-based access | transitaccess-lambda-role |

**Region:** eu-west-1 (Ireland)

## Project Structure

```
Rakesh/
  library/                 Custom Python library (transit-access-nci)
    transit_utils/         Library source
      __init__.py          Exports and version
      route.py             RouteOptimizer (haversine, routing, filtering)
      accessibility.py     AccessibilityChecker (scoring, validation)
      formatter.py         TransitFormatter (display, CSV export)
      validator.py         TransitValidator (input validation, sanitization)
    tests/
      test_transit.py      30+ unit tests
    setup.py               PyPI package config
    README.md              Library documentation

  backend/                 AWS Lambda backend
    lambda_function.py     Single Lambda handler (auth, CRUD, search)
    requirements.txt       Python dependencies

  frontend/                React 19 + Vite + Tailwind v4
    src/
      App.jsx              Main app with routing
      api.js               API client
      pages/               Dashboard, Stops, StopDetail, RoutesPage,
                           RouteDetail, SearchPage, Favorites, Login, Register

  .github/workflows/
    deploy.yml             CI/CD pipeline (test, deploy infrastructure, deploy frontend)

  report/                  IEEE conference paper
```

## Setup and Running

### Prerequisites
- Python 3.11+
- Node.js 20+

### Library
```bash
cd library
pip install -e ".[dev]"
pytest tests/ -v
```

### Backend
The backend is a single AWS Lambda function. For local testing:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
npm run dev          # Development server
npm run build        # Production build
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and receive JWT token

### Stops (CRUD)
- `GET /stops` - List all stops
- `POST /stops` - Create stop (auth required)
- `GET /stops/{id}` - Get stop details
- `PUT /stops/{id}` - Update stop (auth required)
- `DELETE /stops/{id}` - Delete stop (auth required)

### Routes (CRUD)
- `GET /routes` - List all routes
- `POST /routes` - Create route (auth required)
- `GET /routes/{id}` - Get route details
- `PUT /routes/{id}` - Update route (auth required)
- `DELETE /routes/{id}` - Delete route (auth required)

### Search
- `POST /search` - Search routes by origin, destination, and accessibility needs

### Favorites
- `POST /favorites` - Save favorite route
- `GET /favorites` - List favorites
- `DELETE /favorites/{id}` - Remove favorite

### Dashboard
- `GET /dashboard` - Statistics (total stops, routes, accessibility %)

### Notifications
- `POST /subscribe` - Subscribe to email notifications (public)
- `GET /subscribers` - List subscribers (public)

## Accessibility Features

Stops can have the following accessibility features:
- Wheelchair Ramp
- Elevator
- Tactile Paving
- Audio Announcements
- Low Floor Boarding
- Accessible Toilet

## Custom Library: transit-access-nci

- **RouteOptimizer:** Haversine distance calculation, route finding, accessibility filtering, route optimization (fastest/accessible/least transfers)
- **AccessibilityChecker:** Station scoring (0-100), feature filtering, data validation, summary reports
- **TransitFormatter:** Route summaries, station info, schedules, CSV export, accessibility reports
- **TransitValidator:** Stop/route/search validation, input sanitization
