"""
Flask application factory for the Accessible Public Transit Trip Planner.

Author: Rakesh Kunchala (x25176862)
National College of Ireland - Cloud Platform Programming
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from backend.models import db
from backend.config import config_by_name


def create_app(config_name=None):
    """Application factory pattern for creating Flask app instances."""
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    from backend.routes.route_routes import route_bp
    from backend.routes.stop_routes import stop_bp
    from backend.routes.schedule_routes import schedule_bp
    from backend.routes.trip_routes import trip_bp
    from backend.routes.aws_routes import aws_bp

    app.register_blueprint(route_bp)
    app.register_blueprint(stop_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(aws_bp)

    # Root endpoint
    @app.route("/")
    def index():
        return jsonify({
            "application": "Accessible Public Transit Trip Planner",
            "version": "1.0.0",
            "author": "Rakesh Kunchala (x25176862)",
            "student_email": "x25176862@student.ncirl.ie",
            "module": "Cloud Platform Programming",
            "institution": "National College of Ireland",
        })

    @app.route("/health")
    def health():
        return jsonify({"status": "healthy"}), 200

    # Create tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, port=5000)
