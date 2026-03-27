# transit-access-nci

A Python utility library for accessible public transit trip planning.

## Installation

```bash
pip install transit-access-nci
```

## Modules

### RouteOptimizer
Find, filter, and optimize transit routes based on accessibility needs.

```python
from transit_utils import RouteOptimizer

optimizer = RouteOptimizer()
distance = optimizer.calculate_distance(53.35, -6.26, 51.51, -0.13)
routes = optimizer.find_routes(origin, destination, stops)
accessible = optimizer.filter_accessible_routes(routes, ["wheelchair_ramp"])
optimized = optimizer.optimize_route(route, preference="accessible")
```

### AccessibilityChecker
Evaluate station accessibility features and generate reports.

```python
from transit_utils import AccessibilityChecker

checker = AccessibilityChecker()
score = checker.get_accessibility_score(station)
accessible_stations = checker.filter_stations_by_features(stations, ["elevator"])
summary = checker.get_accessibility_summary(stations)
```

### TransitFormatter
Format transit data for display and CSV export.

```python
from transit_utils import TransitFormatter

formatter = TransitFormatter()
print(formatter.format_route_summary(route))
csv_data = formatter.to_csv(stations)
report = formatter.format_accessibility_report(summary)
```

### TransitValidator
Validate and sanitize transit input data.

```python
from transit_utils import TransitValidator

validator = TransitValidator()
valid, errors = validator.validate_stop(stop_data)
valid, errors = validator.validate_route(route_data)
clean = validator.sanitize_input(user_input)
```

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Author

Rakesh Kunchala - National College of Ireland
