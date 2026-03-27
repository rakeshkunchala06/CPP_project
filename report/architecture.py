"""
Generate architecture and component diagrams for the IEEE report.

Author: Rakesh Kunchala (x25176862)
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))


def draw_box(ax, x, y, w, h, text, color='#1a237e', text_color='white', fontsize=9):
    """Draw a labeled box on the axes."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                         facecolor=color, edgecolor='#333', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=text_color, wrap=True)


def draw_arrow(ax, x1, y1, x2, y2, color='#555'):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))


def generate_architecture_diagram():
    """Generate the system architecture diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('System Architecture - Accessible Public Transit Trip Planner\n'
                 'Rakesh Kunchala (x25176862) - NCI Cloud Platform Programming',
                 fontsize=13, fontweight='bold', pad=20)

    # User layer
    draw_box(ax, 5.5, 9, 3, 0.7, 'Users / Browser', '#424242')

    # CloudFront
    draw_arrow(ax, 7, 9, 7, 8.6)
    draw_box(ax, 5, 7.8, 4, 0.7, 'Amazon CloudFront (CDN)', '#ff6f00')

    # Frontend
    draw_arrow(ax, 7, 7.8, 7, 7.3)
    draw_box(ax, 5, 6.5, 4, 0.7, 'React Frontend\n(Dashboard, Trip Planner, Accessibility)', '#1565c0')

    # Arrow to backend
    draw_arrow(ax, 7, 6.5, 7, 6.0)

    # Backend
    draw_box(ax, 4.5, 5.0, 5, 0.8, 'Flask Backend (REST API)\nCRUD: Routes, Stops, Schedules, Trips', '#2e7d32')

    # Custom Library
    draw_arrow(ax, 7, 5.0, 7, 4.5)
    draw_box(ax, 4.5, 3.6, 5, 0.8, 'transitplan Library (Custom OOP)\nPlanner, Accessibility, Fare, Schedule', '#6a1b9a')

    # AWS Services
    draw_arrow(ax, 5.5, 5.0, 2.5, 4.0)
    draw_arrow(ax, 8.5, 5.0, 11.5, 4.0)
    draw_arrow(ax, 5.0, 5.0, 1.5, 2.5)
    draw_arrow(ax, 9.0, 5.0, 12.5, 2.5)
    draw_arrow(ax, 6.0, 5.0, 3.5, 1.3)
    draw_arrow(ax, 8.0, 5.0, 10.5, 1.3)
    draw_arrow(ax, 7.0, 3.6, 7.0, 2.6)

    # AWS Service boxes
    draw_box(ax, 0.5, 3.4, 3.5, 0.7, 'Amazon RDS\n(PostgreSQL)', '#c62828')
    draw_box(ax, 10, 3.4, 3.5, 0.7, 'Amazon S3\n(Static Assets)', '#c62828')
    draw_box(ax, 0.3, 2.0, 3.2, 0.7, 'Amazon SQS\n(Trip Queue)', '#c62828')
    draw_box(ax, 10.5, 2.0, 3.2, 0.7, 'AWS Secrets Mgr\n(API Keys)', '#c62828')
    draw_box(ax, 1.5, 0.7, 3.5, 0.7, 'Amazon Location\n(Maps/Geocoding)', '#c62828')
    draw_box(ax, 9, 0.7, 3.5, 0.7, 'Amazon Comprehend\n(NLP/Sentiment)', '#c62828')
    draw_box(ax, 5.5, 2.0, 3, 0.5, 'SQLite (Local)', '#795548')

    plt.tight_layout()
    path = os.path.join(REPORT_DIR, 'architecture_diagram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Architecture diagram saved: {path}")


def generate_component_diagram():
    """Generate the component/module diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Component Diagram - Accessible Public Transit Trip Planner\n'
                 'Rakesh Kunchala (x25176862)', fontsize=13, fontweight='bold', pad=20)

    # Frontend components
    draw_box(ax, 0.3, 7.5, 2.5, 0.6, 'Dashboard', '#1565c0')
    draw_box(ax, 3.0, 7.5, 2.5, 0.6, 'RoutesPage', '#1565c0')
    draw_box(ax, 5.7, 7.5, 2.5, 0.6, 'StopsPage', '#1565c0')
    draw_box(ax, 8.4, 7.5, 2.5, 0.6, 'TripPlanner', '#1565c0')
    draw_box(ax, 11.1, 7.5, 2.5, 0.6, 'AWSStatus', '#1565c0')
    ax.text(7, 8.3, 'Frontend (React)', fontsize=11, ha='center', fontweight='bold', color='#1565c0')

    # Backend routes
    draw_box(ax, 0.5, 5.8, 2.5, 0.6, '/api/routes', '#2e7d32')
    draw_box(ax, 3.3, 5.8, 2.5, 0.6, '/api/stops', '#2e7d32')
    draw_box(ax, 6.1, 5.8, 2.5, 0.6, '/api/schedules', '#2e7d32')
    draw_box(ax, 8.9, 5.8, 2.5, 0.6, '/api/trips', '#2e7d32')
    draw_box(ax, 11.3, 5.8, 2.3, 0.6, '/api/aws', '#2e7d32')
    ax.text(7, 6.6, 'Backend API (Flask)', fontsize=11, ha='center', fontweight='bold', color='#2e7d32')

    # Models
    draw_box(ax, 0.5, 4.2, 2, 0.6, 'RouteModel', '#e65100')
    draw_box(ax, 2.8, 4.2, 2, 0.6, 'StopModel', '#e65100')
    draw_box(ax, 5.1, 4.2, 2.2, 0.6, 'ScheduleModel', '#e65100')
    draw_box(ax, 7.6, 4.2, 2, 0.6, 'TripModel', '#e65100')
    draw_box(ax, 9.9, 4.2, 3.3, 0.6, 'AccessibilityFeatureModel', '#e65100')
    ax.text(7, 5.0, 'Database Models (SQLAlchemy)', fontsize=11, ha='center', fontweight='bold', color='#e65100')

    # transitplan library
    draw_box(ax, 0.3, 2.5, 2.2, 0.6, 'models.py', '#6a1b9a')
    draw_box(ax, 2.8, 2.5, 2.2, 0.6, 'planner.py', '#6a1b9a')
    draw_box(ax, 5.3, 2.5, 2.6, 0.6, 'accessibility.py', '#6a1b9a')
    draw_box(ax, 8.2, 2.5, 2, 0.6, 'fare.py', '#6a1b9a')
    draw_box(ax, 10.5, 2.5, 3, 0.6, 'schedule_calc.py', '#6a1b9a')
    ax.text(7, 3.3, 'transitplan Library (Custom OOP)', fontsize=11, ha='center', fontweight='bold', color='#6a1b9a')

    # AWS Services
    services = ['RDS', 'S3', 'Location', 'SQS', 'Secrets', 'CloudFront', 'Comprehend']
    for i, svc in enumerate(services):
        x = 0.3 + i * 1.93
        draw_box(ax, x, 0.8, 1.7, 0.6, svc, '#c62828')
    ax.text(7, 1.6, 'AWS Services (7)', fontsize=11, ha='center', fontweight='bold', color='#c62828')

    # Arrows between layers
    for x in [1.5, 4.3, 7, 9.7, 12.3]:
        draw_arrow(ax, x, 7.5, x, 6.5)
    for x in [1.5, 3.8, 6.2, 8.6, 11.5]:
        draw_arrow(ax, x, 5.8, x, 4.9)
    for x in [1.4, 3.9, 6.6, 9.2, 12.0]:
        draw_arrow(ax, x, 4.2, x, 3.2)

    plt.tight_layout()
    path = os.path.join(REPORT_DIR, 'component_diagram.png')
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Component diagram saved: {path}")


if __name__ == "__main__":
    generate_architecture_diagram()
    generate_component_diagram()
