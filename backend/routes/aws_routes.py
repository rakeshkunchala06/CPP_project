"""API endpoints for AWS service status and operations."""

from flask import Blueprint, request, jsonify
from backend.services.rds_service import RDSService
from backend.services.s3_service import S3Service
from backend.services.location_service import LocationService
from backend.services.sqs_service import SQSService
from backend.services.secrets_service import SecretsService
from backend.services.cloudfront_service import CloudFrontService
from backend.services.comprehend_service import ComprehendService

aws_bp = Blueprint("aws", __name__, url_prefix="/api/aws")

# Initialize services in mock mode
rds = RDSService(use_mock=True)
s3 = S3Service(use_mock=True)
location = LocationService(use_mock=True)
sqs = SQSService(use_mock=True)
secrets = SecretsService(use_mock=True)
cloudfront = CloudFrontService(use_mock=True)
comprehend = ComprehendService(use_mock=True)


@aws_bp.route("/status", methods=["GET"])
def get_aws_status():
    """Get health status of all AWS services."""
    return jsonify({
        "services": [
            rds.health_check(),
            s3.health_check(),
            location.health_check(),
            sqs.health_check(),
            secrets.health_check(),
            cloudfront.health_check(),
            comprehend.health_check(),
        ]
    }), 200


@aws_bp.route("/geocode", methods=["POST"])
def geocode():
    """Geocode an address using Amazon Location Service."""
    data = request.get_json()
    if not data or not data.get("address"):
        return jsonify({"error": "address is required"}), 400
    result = location.geocode(data["address"])
    return jsonify(result), 200


@aws_bp.route("/sentiment", methods=["POST"])
def analyze_sentiment():
    """Analyze text sentiment using Amazon Comprehend."""
    data = request.get_json()
    if not data or not data.get("text"):
        return jsonify({"error": "text is required"}), 400
    result = comprehend.analyze_sentiment(data["text"])
    return jsonify(result), 200


@aws_bp.route("/sqs/send", methods=["POST"])
def send_to_queue():
    """Send a trip planning request to SQS."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Message body required"}), 400
    result = sqs.send_message(data)
    return jsonify(result), 200


@aws_bp.route("/sqs/receive", methods=["GET"])
def receive_from_queue():
    """Receive messages from SQS."""
    messages = sqs.receive_messages()
    return jsonify({"messages": messages}), 200


@aws_bp.route("/s3/upload", methods=["POST"])
def upload_to_s3():
    """Upload data to S3."""
    data = request.get_json()
    if not data or not data.get("key"):
        return jsonify({"error": "key is required"}), 400
    result = s3.upload_file(data["key"], data.get("data", ""))
    return jsonify(result), 200


@aws_bp.route("/s3/files", methods=["GET"])
def list_s3_files():
    """List files in S3."""
    prefix = request.args.get("prefix", "")
    files = s3.list_files(prefix)
    return jsonify({"files": files}), 200
