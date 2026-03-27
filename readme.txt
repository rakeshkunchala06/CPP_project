================================================================================
  ACCESSIBLE PUBLIC TRANSIT TRIP PLANNER
  Cloud Platform Programming - National College of Ireland
================================================================================

Student:    Rakesh Kunchala
Student ID: x25176862
Email:      x25176862@student.ncirl.ie
Module:     Cloud Platform Programming

================================================================================
  PROJECT OVERVIEW
================================================================================

A cloud-native accessible public transit trip planner that integrates 7 AWS
services, implements a custom OOP Python library (transitplan), and provides
full CRUD operations through a Flask REST API with a React frontend.

================================================================================
  AWS SERVICES (7)
================================================================================

1. Amazon RDS (PostgreSQL) - Database for routes, stops, schedules
2. Amazon S3              - Static assets and map data storage
3. Amazon Location Service - Maps and geocoding
4. Amazon SQS             - Trip planning request queue
5. AWS Secrets Manager     - API keys and credentials storage
6. Amazon CloudFront       - CDN for frontend delivery
7. Amazon Comprehend       - User feedback sentiment analysis

All services work in LOCAL MOCK MODE for development and testing.

================================================================================
  PROJECT STRUCTURE
================================================================================

Rakesh/
  backend/             Flask REST API application
    app.py             Application factory (create_app)
    config.py          Development/Testing/Production configs
    models/            SQLAlchemy models (Route, Stop, Schedule, Trip, AccessibilityFeature)
    routes/            CRUD API endpoints + AWS service endpoints
    services/          AWS service wrappers (7 services, all with mock mode)
    tests/             35 integration tests
    requirements.txt   Python dependencies

  frontend/            React single-page application
    src/pages/         7 pages (Dashboard, Routes, Stops, Schedules, TripPlanner, Accessibility, AWSStatus)
    public/            Static HTML
    package.json       Node dependencies

  transitplan/         Custom OOP Python library
    transitplan/       Library source code
      models.py        Stop, Route, Schedule, Connection, TransitNetwork
      planner.py       TripPlanner (Dijkstra shortest path, fewest transfers)
      accessibility.py AccessibilityScorer (weighted scoring system)
      fare.py          FareCalculator (flat, zone-based, distance-based)
      schedule_calc.py ScheduleCalculator (time arithmetic, next departures)
    tests/             70 unit tests
    setup.py           Package configuration

  report/              IEEE conference paper
    main.tex           LaTeX source (IEEE format)
    main.pdf           Compiled PDF report
    architecture.py    Diagram generation script
    architecture_diagram.png
    component_diagram.png

  venv/                Python virtual environment
  .gitignore           Git ignore rules
  readme.txt           This file

================================================================================
  SETUP AND RUNNING
================================================================================

Prerequisites: Python 3.8+, Node.js 16+

1. Backend Setup:
   cd Rakesh
   source venv/bin/activate          (or: python3 -m venv venv && source venv/bin/activate)
   pip install -r backend/requirements.txt
   pip install -e transitplan/
   python -m flask --app backend.app run

2. Frontend Setup:
   cd Rakesh/frontend
   npm install
   npm start                         (development server on port 3000)
   npm run build                     (production build)

3. Run All Tests:
   source venv/bin/activate
   python -m pytest transitplan/tests/ -v     (70 library unit tests)
   python -m pytest backend/tests/ -v         (35 API integration tests)

   Total: 105 tests, all passing

4. Generate Report Diagrams:
   python report/architecture.py

5. Compile LaTeX Report:
   cd report && pdflatex main.tex

================================================================================
  CRUD OPERATIONS
================================================================================

Routes:    POST/GET/PUT/DELETE  /api/routes
Stops:     POST/GET/PUT/DELETE  /api/stops
Schedules: POST/GET/PUT/DELETE  /api/schedules
Trips:     POST/GET/PUT/DELETE  /api/trips

AWS:       GET  /api/aws/status
           POST /api/aws/geocode
           POST /api/aws/sentiment
           POST /api/aws/sqs/send
           GET  /api/aws/sqs/receive

================================================================================
  CUSTOM LIBRARY: transitplan
================================================================================

- Route modeling with graph-based TransitNetwork
- Trip planning using Dijkstra's algorithm (shortest path and fewest transfers)
- Accessibility scoring: wheelchair (40%), audio (25%), visual (20%), tactile (15%)
- Fare estimation: flat, zone-based, and distance-based models
- Schedule calculations: time arithmetic, next departures, conflict detection
- Transfer point detection across multi-route networks

================================================================================
