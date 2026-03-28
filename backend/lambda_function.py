"""
TransitAccess - Accessible Public Transit Trip Planner
Single AWS Lambda function handling all API routes.
DynamoDB table uses single partition key: id (String)
Each item has entityType field: user, stop, route, favorite, search
"""

import json
import os
import uuid
import hashlib
import hmac
import time
import base64
import decimal
import re
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Attr

# ---------------------------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------------------------
REGION = os.environ.get("REGION", "eu-west-1")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "transitaccess-prod")
S3_BUCKET = os.environ.get("S3_BUCKET", "transitaccess-files-prod-rakesh")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
JWT_SECRET = os.environ.get("JWT_SECRET", "transitaccess-secret-2026")

# AWS clients
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
s3 = boto3.client("s3", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def convert_decimals(obj):
    """Recursively convert Decimal types to int/float for JSON serialization."""
    if isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj


def json_response(status_code, body):
    """Build a standard API Gateway response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(convert_decimals(body), default=str),
    }


def parse_body(event):
    """Parse the JSON body from the event."""
    body = event.get("body", "{}")
    if isinstance(body, str):
        try:
            return json.loads(body)
        except (json.JSONDecodeError, TypeError):
            return {}
    return body if body else {}


def get_path(event):
    """Extract the resource path."""
    return event.get("path", "") or event.get("rawPath", "")


def get_method(event):
    """Extract the HTTP method."""
    return (
        event.get("httpMethod", "")
        or event.get("requestContext", {}).get("http", {}).get("method", "")
    ).upper()


def get_path_param(path, prefix):
    """Extract ID from path like /stops/{id} given prefix /stops/."""
    if path.startswith(prefix):
        return path[len(prefix):]
    return None


def get_auth_token(event):
    """Extract the Bearer token from the Authorization header."""
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def to_decimal(val):
    """Convert a numeric value to Decimal for DynamoDB."""
    return decimal.Decimal(str(val))


def scan_all(filter_expression):
    """Scan with pagination to get all matching items."""
    items = []
    params = {"FilterExpression": filter_expression}
    while True:
        resp = table.scan(**params)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            break
        params["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


# ---------------------------------------------------------------------------
# Auth helpers (PBKDF2 + JWT)
# ---------------------------------------------------------------------------

def hash_password(password, salt=None):
    """Hash password with PBKDF2-HMAC-SHA256."""
    if salt is None:
        salt = uuid.uuid4().hex
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return salt, dk.hex()


def verify_password(password, salt, hashed):
    """Verify a password against its hash."""
    _, new_hash = hash_password(password, salt)
    return hmac.compare_digest(new_hash, hashed)


def create_token(user_id, email):
    """Create a JWT token: base64(header).base64(payload).hmac_signature."""
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps({
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + 86400,
    })
    h = base64.urlsafe_b64encode(header.encode()).decode().rstrip("=")
    p = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    sig_input = f"{h}.{p}"
    signature = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).hexdigest()
    return f"{h}.{p}.{signature}"


def decode_token(token):
    """Decode and verify the JWT token. Returns payload dict or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        h, p, sig = parts
        sig_input = f"{h}.{p}"
        expected = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        padding = 4 - len(p) % 4
        payload = json.loads(base64.urlsafe_b64decode(p + "=" * padding))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def require_auth(event):
    """Verify auth token and return user payload or error response."""
    token = get_auth_token(event)
    if not token:
        return None, json_response(401, {"error": "Authorization token required"})
    payload = decode_token(token)
    if not payload:
        return None, json_response(401, {"error": "Invalid or expired token"})
    return payload, None


# ---------------------------------------------------------------------------
# Route handlers
# ---------------------------------------------------------------------------

# ---- Auth ----

def handle_register(event):
    body = parse_body(event)
    username = body.get("username", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return json_response(400, {"error": "Email and password are required"})
    if len(password) < 6:
        return json_response(400, {"error": "Password must be at least 6 characters"})

    # Check if user exists by scanning for email
    try:
        existing = scan_all(
            Attr("entityType").eq("user") & Attr("email").eq(email)
        )
        if existing:
            return json_response(409, {"error": "Email already registered"})
    except Exception:
        pass

    user_id = str(uuid.uuid4())
    salt, hashed = hash_password(password)
    now = datetime.utcnow().isoformat()

    table.put_item(Item={
        "id": user_id,
        "entityType": "user",
        "username": username,
        "email": email,
        "passwordHash": hashed,
        "passwordSalt": salt,
        "createdAt": now,
    })

    token = create_token(user_id, email)
    return json_response(201, {
        "message": "Registration successful",
        "token": token,
        "user": {"userId": user_id, "email": email, "username": username},
    })


def handle_login(event):
    body = parse_body(event)
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return json_response(400, {"error": "Email and password are required"})

    # Find user by scanning for email
    try:
        users = scan_all(
            Attr("entityType").eq("user") & Attr("email").eq(email)
        )
        if not users:
            return json_response(401, {"error": "Invalid email or password"})
        item = users[0]
    except Exception as e:
        return json_response(500, {"error": str(e)})

    if not verify_password(password, item["passwordSalt"], item["passwordHash"]):
        return json_response(401, {"error": "Invalid email or password"})

    token = create_token(item["id"], email)
    return json_response(200, {
        "message": "Login successful",
        "token": token,
        "user": {"userId": item["id"], "email": email, "username": item.get("username", "")},
    })


# ---- Stops ----

def handle_get_stops(event):
    user, err = require_auth(event)
    if err:
        return err

    try:
        stops = scan_all(Attr("entityType").eq("stop"))
        return json_response(200, {"stops": stops, "count": len(stops)})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_create_stop(event):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    name = body.get("name", "").strip()
    if not name:
        return json_response(400, {"error": "Stop name is required"})

    stop_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    item = {
        "id": stop_id,
        "entityType": "stop",
        "name": name,
        "latitude": to_decimal(body.get("latitude", 0)),
        "longitude": to_decimal(body.get("longitude", 0)),
        "address": body.get("address", ""),
        "accessibilityFeatures": body.get("accessibilityFeatures", []),
        "transitTypes": body.get("transitTypes", []),
        "createdBy": user["user_id"],
        "createdAt": now,
        "updatedAt": now,
    }

    table.put_item(Item=item)
    return json_response(201, {"message": "Stop created", "stop": item})


def handle_get_stop(event, stop_id):
    user, err = require_auth(event)
    if err:
        return err

    try:
        resp = table.get_item(Key={"id": stop_id})
        item = resp.get("Item")
        if not item or item.get("entityType") != "stop":
            return json_response(404, {"error": "Stop not found"})
        return json_response(200, {"stop": item})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_update_stop(event, stop_id):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    now = datetime.utcnow().isoformat()

    update_expr_parts = ["#updatedAt = :updatedAt"]
    expr_names = {"#updatedAt": "updatedAt"}
    expr_values = {":updatedAt": now}

    field_map = {
        "name": "name",
        "latitude": "latitude",
        "longitude": "longitude",
        "address": "address",
        "accessibilityFeatures": "accessibilityFeatures",
        "transitTypes": "transitTypes",
    }

    for field, attr in field_map.items():
        if field in body:
            placeholder = f":{field}"
            expr_alias = f"#{field}"
            val = body[field]
            if field in ("latitude", "longitude"):
                val = to_decimal(val)
            update_expr_parts.append(f"{expr_alias} = {placeholder}")
            expr_names[expr_alias] = attr
            expr_values[placeholder] = val

    expr_values[":et"] = "stop"

    try:
        resp = table.update_item(
            Key={"id": stop_id},
            UpdateExpression="SET " + ", ".join(update_expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
            ConditionExpression="attribute_exists(id) AND entityType = :et",
        )
        return json_response(200, {"message": "Stop updated", "stop": resp["Attributes"]})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Stop not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_delete_stop(event, stop_id):
    user, err = require_auth(event)
    if err:
        return err

    try:
        table.delete_item(
            Key={"id": stop_id},
            ConditionExpression="attribute_exists(id) AND entityType = :et",
            ExpressionAttributeValues={":et": "stop"},
        )
        return json_response(200, {"message": "Stop deleted"})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Stop not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


# ---- Routes ----

def handle_get_routes(event):
    user, err = require_auth(event)
    if err:
        return err

    try:
        routes = scan_all(Attr("entityType").eq("route"))
        return json_response(200, {"routes": routes, "count": len(routes)})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_create_route(event):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    name = body.get("name", "").strip()
    if not name:
        return json_response(400, {"error": "Route name is required"})

    route_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    rating = body.get("accessibilityRating", 3)
    try:
        rating = int(rating)
        rating = max(1, min(5, rating))
    except (ValueError, TypeError):
        rating = 3

    item = {
        "id": route_id,
        "entityType": "route",
        "name": name,
        "origin": body.get("origin", ""),
        "destination": body.get("destination", ""),
        "stops": body.get("stops", []),
        "transitType": body.get("transitType", "bus"),
        "schedule": body.get("schedule", {}),
        "accessibilityRating": rating,
        "createdBy": user["user_id"],
        "createdAt": now,
        "updatedAt": now,
    }

    table.put_item(Item=item)
    return json_response(201, {"message": "Route created", "route": item})


def handle_get_route(event, route_id):
    user, err = require_auth(event)
    if err:
        return err

    try:
        resp = table.get_item(Key={"id": route_id})
        item = resp.get("Item")
        if not item or item.get("entityType") != "route":
            return json_response(404, {"error": "Route not found"})
        return json_response(200, {"route": item})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_update_route(event, route_id):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    now = datetime.utcnow().isoformat()

    update_expr_parts = ["#updatedAt = :updatedAt"]
    expr_names = {"#updatedAt": "updatedAt"}
    expr_values = {":updatedAt": now}

    field_map = {
        "name": "name",
        "origin": "origin",
        "destination": "destination",
        "stops": "stops",
        "transitType": "transitType",
        "schedule": "schedule",
        "accessibilityRating": "accessibilityRating",
    }

    for field, attr in field_map.items():
        if field in body:
            placeholder = f":{field}"
            expr_alias = f"#{field}"
            val = body[field]
            if field == "accessibilityRating":
                try:
                    val = max(1, min(5, int(val)))
                except (ValueError, TypeError):
                    val = 3
            update_expr_parts.append(f"{expr_alias} = {placeholder}")
            expr_names[expr_alias] = attr
            expr_values[placeholder] = val

    try:
        resp = table.update_item(
            Key={"id": route_id},
            UpdateExpression="SET " + ", ".join(update_expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues={**expr_values, ":et": "route"},
            ReturnValues="ALL_NEW",
            ConditionExpression="attribute_exists(id) AND entityType = :et",
        )
        return json_response(200, {"message": "Route updated", "route": resp["Attributes"]})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Route not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_delete_route(event, route_id):
    user, err = require_auth(event)
    if err:
        return err

    try:
        table.delete_item(
            Key={"id": route_id},
            ConditionExpression="attribute_exists(id) AND entityType = :et",
            ExpressionAttributeValues={":et": "route"},
        )
        return json_response(200, {"message": "Route deleted"})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Route not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


# ---- Search ----

def handle_search(event):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    origin = body.get("origin", "").strip()
    destination = body.get("destination", "").strip()
    needs = body.get("accessibilityNeeds", [])

    if not origin or not destination:
        return json_response(400, {"error": "Origin and destination are required"})

    # Get all routes
    try:
        all_routes = scan_all(Attr("entityType").eq("route"))
    except Exception as e:
        return json_response(500, {"error": str(e)})

    # Filter by origin/destination (partial match)
    matched = []
    for route in all_routes:
        r_origin = route.get("origin", "").lower()
        r_dest = route.get("destination", "").lower()
        if origin.lower() in r_origin or origin.lower() in r_dest:
            if destination.lower() in r_dest or destination.lower() in r_origin:
                matched.append(route)

    # Filter by accessibility needs
    if needs:
        filtered = []
        for route in matched:
            stop_ids = route.get("stops", [])
            all_meet = True
            for sid in stop_ids:
                try:
                    sr = table.get_item(Key={"id": sid})
                    stop = sr.get("Item", {})
                    if stop.get("entityType") != "stop":
                        all_meet = False
                        break
                    features = stop.get("accessibilityFeatures", [])
                    if not all(n in features for n in needs):
                        all_meet = False
                        break
                except Exception:
                    all_meet = False
                    break
            if all_meet:
                filtered.append(route)
        matched = filtered

    # Save search history
    try:
        search_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        table.put_item(Item={
            "id": search_id,
            "entityType": "search",
            "userId": user["user_id"],
            "email": user["email"],
            "origin": origin,
            "destination": destination,
            "accessibilityNeeds": needs,
            "resultCount": len(matched),
            "createdAt": now,
        })
    except Exception:
        pass

    return json_response(200, {
        "results": matched,
        "count": len(matched),
        "search": {"origin": origin, "destination": destination, "accessibilityNeeds": needs},
    })


# ---- Favorites ----

def handle_add_favorite(event):
    user, err = require_auth(event)
    if err:
        return err

    body = parse_body(event)
    route_id = body.get("routeId", "").strip()
    if not route_id:
        return json_response(400, {"error": "routeId is required"})

    fav_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    table.put_item(Item={
        "id": fav_id,
        "entityType": "favorite",
        "userId": user["user_id"],
        "email": user["email"],
        "routeId": route_id,
        "createdAt": now,
    })

    return json_response(201, {"message": "Favorite added", "favoriteId": fav_id})


def handle_get_favorites(event):
    user, err = require_auth(event)
    if err:
        return err

    try:
        favorites = scan_all(
            Attr("entityType").eq("favorite") & Attr("userId").eq(user["user_id"])
        )

        # Enrich with route details
        for fav in favorites:
            rid = fav.get("routeId", "")
            try:
                rr = table.get_item(Key={"id": rid})
                route_item = rr.get("Item", {})
                if route_item.get("entityType") == "route":
                    fav["route"] = route_item
                else:
                    fav["route"] = {}
            except Exception:
                fav["route"] = {}

        return json_response(200, {"favorites": favorites, "count": len(favorites)})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_delete_favorite(event, fav_id):
    user, err = require_auth(event)
    if err:
        return err

    try:
        table.delete_item(
            Key={"id": fav_id},
            ConditionExpression="attribute_exists(id) AND entityType = :et AND userId = :uid",
            ExpressionAttributeValues={":et": "favorite", ":uid": user["user_id"]},
        )
        return json_response(200, {"message": "Favorite removed"})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Favorite not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


# ---- Dashboard ----

def handle_dashboard(event):
    user, err = require_auth(event)
    if err:
        return err

    # Count stops
    try:
        all_stops = scan_all(Attr("entityType").eq("stop"))
        total_stops = len(all_stops)
    except Exception:
        all_stops = []
        total_stops = 0

    # Count routes
    try:
        all_routes = scan_all(Attr("entityType").eq("route"))
        total_routes = len(all_routes)
    except Exception:
        total_routes = 0

    # Calculate accessible stops percentage
    accessible_pct = 0
    if all_stops:
        accessible = sum(
            1 for s in all_stops if len(s.get("accessibilityFeatures", [])) >= 3
        )
        accessible_pct = round((accessible / len(all_stops)) * 100, 1)

    # Recent searches for this user
    recent_searches = []
    try:
        searches = scan_all(
            Attr("entityType").eq("search") & Attr("userId").eq(user["user_id"])
        )
        # Sort by createdAt descending, take top 5
        searches.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        recent_searches = searches[:5]
    except Exception:
        pass

    return json_response(200, {
        "totalStops": total_stops,
        "totalRoutes": total_routes,
        "accessibleStopsPct": accessible_pct,
        "recentSearches": recent_searches,
    })


# ---- Notifications (SNS) - PUBLIC ----

def handle_subscribe(event):
    body = parse_body(event)
    email = body.get("email", "").strip()

    if not email:
        return json_response(400, {"error": "Email is required"})

    if not SNS_TOPIC_ARN:
        return json_response(500, {"error": "SNS topic not configured"})

    try:
        resp = sns.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol="email",
            Endpoint=email,
        )
        return json_response(201, {
            "message": "Subscription request sent. Please confirm via email.",
            "subscriptionArn": resp.get("SubscriptionArn", "pending"),
        })
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_get_subscribers(event):
    if not SNS_TOPIC_ARN:
        return json_response(500, {"error": "SNS topic not configured"})

    try:
        resp = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        subs = [
            {
                "endpoint": s.get("Endpoint", ""),
                "protocol": s.get("Protocol", ""),
                "status": "confirmed" if s.get("SubscriptionArn", "").startswith("arn:") else "pending",
            }
            for s in resp.get("Subscriptions", [])
        ]
        return json_response(200, {"subscribers": subs, "count": len(subs)})
    except Exception as e:
        return json_response(500, {"error": str(e)})


# ---------------------------------------------------------------------------
# Lambda handler / router
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    """Main Lambda entry point. Routes requests to appropriate handlers."""
    method = get_method(event)
    path = get_path(event)

    # Handle CORS preflight
    if method == "OPTIONS":
        return json_response(200, {"message": "OK"})

    try:
        # --- PUBLIC routes (before auth check) ---

        # Notifications (PUBLIC)
        if path == "/subscribe" and method == "POST":
            return handle_subscribe(event)
        if path == "/subscribers" and method == "GET":
            return handle_get_subscribers(event)

        # Auth routes (PUBLIC)
        if path == "/auth/register" and method == "POST":
            return handle_register(event)
        if path == "/auth/login" and method == "POST":
            return handle_login(event)

        # --- PROTECTED routes (auth checked inside each handler) ---

        # Stop routes
        if path == "/stops" and method == "GET":
            return handle_get_stops(event)
        if path == "/stops" and method == "POST":
            return handle_create_stop(event)
        stop_match = re.match(r"^/stops/([\w-]+)$", path)
        if stop_match:
            stop_id = stop_match.group(1)
            if method == "GET":
                return handle_get_stop(event, stop_id)
            if method == "PUT":
                return handle_update_stop(event, stop_id)
            if method == "DELETE":
                return handle_delete_stop(event, stop_id)

        # Route routes
        if path == "/routes" and method == "GET":
            return handle_get_routes(event)
        if path == "/routes" and method == "POST":
            return handle_create_route(event)
        route_match = re.match(r"^/routes/([\w-]+)$", path)
        if route_match:
            route_id = route_match.group(1)
            if method == "GET":
                return handle_get_route(event, route_id)
            if method == "PUT":
                return handle_update_route(event, route_id)
            if method == "DELETE":
                return handle_delete_route(event, route_id)

        # Search
        if path == "/search" and method == "POST":
            return handle_search(event)

        # Favorites
        if path == "/favorites" and method == "POST":
            return handle_add_favorite(event)
        if path == "/favorites" and method == "GET":
            return handle_get_favorites(event)
        fav_match = re.match(r"^/favorites/([\w-]+)$", path)
        if fav_match:
            fav_id = fav_match.group(1)
            if method == "DELETE":
                return handle_delete_favorite(event, fav_id)

        # Dashboard
        if path == "/dashboard" and method == "GET":
            return handle_dashboard(event)

        return json_response(404, {"error": f"Route not found: {method} {path}"})

    except Exception as e:
        return json_response(500, {"error": f"Internal server error: {str(e)}"})
