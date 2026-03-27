"""
TransitAccess - Accessible Public Transit Trip Planner
Single AWS Lambda function handling all API routes.
"""

import json
import os
import uuid
import hashlib
import hmac
import time
import decimal
import re
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr

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

class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types returned by DynamoDB."""
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


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
        "body": json.dumps(body, cls=DecimalEncoder),
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


def get_path_param(event, name):
    """Extract a path parameter."""
    params = event.get("pathParameters") or {}
    return params.get(name)


def get_query_params(event):
    """Extract query string parameters."""
    return event.get("queryStringParameters") or {}


def get_auth_token(event):
    """Extract the Bearer token from the Authorization header."""
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


# ---------------------------------------------------------------------------
# Auth helpers (PBKDF2 + simple JWT-like token)
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
    """Create a simple JWT-like token (header.payload.signature)."""
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps({
        "user_id": user_id,
        "email": email,
        "exp": int(time.time()) + 86400,
    })
    import base64
    h = base64.urlsafe_b64encode(header.encode()).decode().rstrip("=")
    p = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    sig_input = f"{h}.{p}"
    signature = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).hexdigest()
    return f"{h}.{p}.{signature}"


def decode_token(token):
    """Decode and verify the token. Returns payload dict or None."""
    import base64
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
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")
    name = body.get("name", "").strip()

    if not email or not password:
        return json_response(400, {"error": "Email and password are required"})
    if len(password) < 6:
        return json_response(400, {"error": "Password must be at least 6 characters"})

    # Check if user exists
    try:
        resp = table.get_item(Key={"PK": f"USER#{email}", "SK": "PROFILE"})
        if "Item" in resp:
            return json_response(409, {"error": "Email already registered"})
    except Exception:
        pass

    user_id = str(uuid.uuid4())
    salt, hashed = hash_password(password)

    table.put_item(Item={
        "PK": f"USER#{email}",
        "SK": "PROFILE",
        "userId": user_id,
        "email": email,
        "name": name,
        "passwordHash": hashed,
        "passwordSalt": salt,
        "createdAt": datetime.utcnow().isoformat(),
    })

    token = create_token(user_id, email)
    return json_response(201, {
        "message": "Registration successful",
        "token": token,
        "user": {"userId": user_id, "email": email, "name": name},
    })


def handle_login(event):
    body = parse_body(event)
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return json_response(400, {"error": "Email and password are required"})

    try:
        resp = table.get_item(Key={"PK": f"USER#{email}", "SK": "PROFILE"})
        item = resp.get("Item")
        if not item:
            return json_response(401, {"error": "Invalid email or password"})
    except Exception as e:
        return json_response(500, {"error": str(e)})

    if not verify_password(password, item["passwordSalt"], item["passwordHash"]):
        return json_response(401, {"error": "Invalid email or password"})

    token = create_token(item["userId"], email)
    return json_response(200, {
        "message": "Login successful",
        "token": token,
        "user": {"userId": item["userId"], "email": email, "name": item.get("name", "")},
    })


# ---- Stops ----

def handle_get_stops(event):
    try:
        resp = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("STOPS"),
        )
        stops = resp.get("Items", [])
        return json_response(200, {"stops": stops, "count": len(stops)})
    except Exception:
        # Fallback: scan for stops
        resp = table.scan(FilterExpression=Attr("PK").begins_with("STOP#"))
        items = [i for i in resp.get("Items", []) if i.get("SK") == "METADATA"]
        return json_response(200, {"stops": items, "count": len(items)})


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
        "PK": f"STOP#{stop_id}",
        "SK": "METADATA",
        "GSI1PK": "STOPS",
        "GSI1SK": name,
        "stopId": stop_id,
        "name": name,
        "latitude": body.get("latitude", 0),
        "longitude": body.get("longitude", 0),
        "address": body.get("address", ""),
        "accessibilityFeatures": body.get("accessibilityFeatures", []),
        "transitTypes": body.get("transitTypes", []),
        "createdBy": user["user_id"],
        "createdAt": now,
        "updatedAt": now,
    }

    # Convert floats to Decimal for DynamoDB
    item["latitude"] = decimal.Decimal(str(item["latitude"]))
    item["longitude"] = decimal.Decimal(str(item["longitude"]))

    table.put_item(Item=item)
    return json_response(201, {"message": "Stop created", "stop": item})


def handle_get_stop(event):
    stop_id = get_path_param(event, "id")
    if not stop_id:
        return json_response(400, {"error": "Stop ID is required"})

    try:
        resp = table.get_item(Key={"PK": f"STOP#{stop_id}", "SK": "METADATA"})
        item = resp.get("Item")
        if not item:
            return json_response(404, {"error": "Stop not found"})
        return json_response(200, {"stop": item})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_update_stop(event):
    user, err = require_auth(event)
    if err:
        return err

    stop_id = get_path_param(event, "id")
    if not stop_id:
        return json_response(400, {"error": "Stop ID is required"})

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
                val = decimal.Decimal(str(val))
            update_expr_parts.append(f"{expr_alias} = {placeholder}")
            expr_names[expr_alias] = attr
            expr_values[placeholder] = val

    try:
        resp = table.update_item(
            Key={"PK": f"STOP#{stop_id}", "SK": "METADATA"},
            UpdateExpression="SET " + ", ".join(update_expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
            ConditionExpression="attribute_exists(PK)",
        )
        return json_response(200, {"message": "Stop updated", "stop": resp["Attributes"]})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return json_response(404, {"error": "Stop not found"})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_delete_stop(event):
    user, err = require_auth(event)
    if err:
        return err

    stop_id = get_path_param(event, "id")
    if not stop_id:
        return json_response(400, {"error": "Stop ID is required"})

    try:
        table.delete_item(
            Key={"PK": f"STOP#{stop_id}", "SK": "METADATA"},
            ConditionExpression="attribute_exists(PK)",
        )
        return json_response(200, {"message": "Stop deleted"})
    except Exception:
        return json_response(404, {"error": "Stop not found"})


# ---- Routes ----

def handle_get_routes(event):
    try:
        resp = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROUTES"),
        )
        routes = resp.get("Items", [])
        return json_response(200, {"routes": routes, "count": len(routes)})
    except Exception:
        resp = table.scan(FilterExpression=Attr("PK").begins_with("ROUTE#"))
        items = [i for i in resp.get("Items", []) if i.get("SK") == "METADATA"]
        return json_response(200, {"routes": items, "count": len(items)})


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
        "PK": f"ROUTE#{route_id}",
        "SK": "METADATA",
        "GSI1PK": "ROUTES",
        "GSI1SK": name,
        "routeId": route_id,
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


def handle_get_route(event):
    route_id = get_path_param(event, "id")
    if not route_id:
        return json_response(400, {"error": "Route ID is required"})

    try:
        resp = table.get_item(Key={"PK": f"ROUTE#{route_id}", "SK": "METADATA"})
        item = resp.get("Item")
        if not item:
            return json_response(404, {"error": "Route not found"})
        return json_response(200, {"route": item})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_update_route(event):
    user, err = require_auth(event)
    if err:
        return err

    route_id = get_path_param(event, "id")
    if not route_id:
        return json_response(400, {"error": "Route ID is required"})

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
            Key={"PK": f"ROUTE#{route_id}", "SK": "METADATA"},
            UpdateExpression="SET " + ", ".join(update_expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ReturnValues="ALL_NEW",
            ConditionExpression="attribute_exists(PK)",
        )
        return json_response(200, {"message": "Route updated", "route": resp["Attributes"]})
    except Exception:
        return json_response(404, {"error": "Route not found"})


def handle_delete_route(event):
    user, err = require_auth(event)
    if err:
        return err

    route_id = get_path_param(event, "id")
    if not route_id:
        return json_response(400, {"error": "Route ID is required"})

    try:
        table.delete_item(
            Key={"PK": f"ROUTE#{route_id}", "SK": "METADATA"},
            ConditionExpression="attribute_exists(PK)",
        )
        return json_response(200, {"message": "Route deleted"})
    except Exception:
        return json_response(404, {"error": "Route not found"})


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

    # Query all routes
    try:
        resp = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROUTES"),
        )
        all_routes = resp.get("Items", [])
    except Exception:
        resp = table.scan(FilterExpression=Attr("PK").begins_with("ROUTE#"))
        all_routes = [i for i in resp.get("Items", []) if i.get("SK") == "METADATA"]

    # Filter by origin/destination (partial match)
    matched = []
    for route in all_routes:
        r_origin = route.get("origin", "").lower()
        r_dest = route.get("destination", "").lower()
        if origin.lower() in r_origin or origin.lower() in r_dest:
            if destination.lower() in r_dest or destination.lower() in r_origin:
                matched.append(route)

    # Filter by accessibility needs: check that route accessibility rating
    # is high enough, and fetch stop details for accessibility features
    if needs:
        filtered = []
        for route in matched:
            stop_ids = route.get("stops", [])
            all_meet = True
            for sid in stop_ids:
                try:
                    sr = table.get_item(Key={"PK": f"STOP#{sid}", "SK": "METADATA"})
                    stop = sr.get("Item", {})
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
        table.put_item(Item={
            "PK": f"USER#{user['email']}",
            "SK": f"SEARCH#{datetime.utcnow().isoformat()}",
            "origin": origin,
            "destination": destination,
            "accessibilityNeeds": needs,
            "resultCount": len(matched),
            "timestamp": datetime.utcnow().isoformat(),
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
        "PK": f"USER#{user['email']}",
        "SK": f"FAV#{fav_id}",
        "favoriteId": fav_id,
        "routeId": route_id,
        "createdAt": now,
    })

    return json_response(201, {"message": "Favorite added", "favoriteId": fav_id})


def handle_get_favorites(event):
    user, err = require_auth(event)
    if err:
        return err

    try:
        resp = table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{user['email']}")
            & Key("SK").begins_with("FAV#"),
        )
        favorites = resp.get("Items", [])

        # Enrich with route details
        for fav in favorites:
            rid = fav.get("routeId", "")
            try:
                rr = table.get_item(Key={"PK": f"ROUTE#{rid}", "SK": "METADATA"})
                fav["route"] = rr.get("Item", {})
            except Exception:
                fav["route"] = {}

        return json_response(200, {"favorites": favorites, "count": len(favorites)})
    except Exception as e:
        return json_response(500, {"error": str(e)})


def handle_delete_favorite(event):
    user, err = require_auth(event)
    if err:
        return err

    fav_id = get_path_param(event, "id")
    if not fav_id:
        return json_response(400, {"error": "Favorite ID is required"})

    try:
        table.delete_item(
            Key={"PK": f"USER#{user['email']}", "SK": f"FAV#{fav_id}"},
            ConditionExpression="attribute_exists(PK)",
        )
        return json_response(200, {"message": "Favorite removed"})
    except Exception:
        return json_response(404, {"error": "Favorite not found"})


# ---- Dashboard ----

def handle_dashboard(event):
    user, err = require_auth(event)
    if err:
        return err

    try:
        # Count stops
        stops_resp = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("STOPS"),
            Select="COUNT",
        )
        total_stops = stops_resp.get("Count", 0)
    except Exception:
        total_stops = 0

    try:
        # Count routes
        routes_resp = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROUTES"),
            Select="COUNT",
        )
        total_routes = routes_resp.get("Count", 0)
    except Exception:
        total_routes = 0

    # Calculate accessible stops percentage
    accessible_pct = 0
    try:
        stops_data = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("STOPS"),
        )
        all_stops = stops_data.get("Items", [])
        if all_stops:
            accessible = sum(
                1 for s in all_stops if len(s.get("accessibilityFeatures", [])) >= 3
            )
            accessible_pct = round((accessible / len(all_stops)) * 100, 1)
    except Exception:
        pass

    # Recent searches
    recent_searches = []
    try:
        search_resp = table.query(
            KeyConditionExpression=Key("PK").eq(f"USER#{user['email']}")
            & Key("SK").begins_with("SEARCH#"),
            ScanIndexForward=False,
            Limit=5,
        )
        recent_searches = search_resp.get("Items", [])
    except Exception:
        pass

    return json_response(200, {
        "totalStops": total_stops,
        "totalRoutes": total_routes,
        "accessibleStopsPct": accessible_pct,
        "recentSearches": recent_searches,
    })


# ---- Notifications (SNS) ----

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
        # Auth routes
        if path == "/register" and method == "POST":
            return handle_register(event)
        if path == "/login" and method == "POST":
            return handle_login(event)

        # Stop routes
        if path == "/stops" and method == "GET":
            return handle_get_stops(event)
        if path == "/stops" and method == "POST":
            return handle_create_stop(event)
        if re.match(r"^/stops/[\w-]+$", path):
            if method == "GET":
                return handle_get_stop(event)
            if method == "PUT":
                return handle_update_stop(event)
            if method == "DELETE":
                return handle_delete_stop(event)

        # Route routes
        if path == "/routes" and method == "GET":
            return handle_get_routes(event)
        if path == "/routes" and method == "POST":
            return handle_create_route(event)
        if re.match(r"^/routes/[\w-]+$", path):
            if method == "GET":
                return handle_get_route(event)
            if method == "PUT":
                return handle_update_route(event)
            if method == "DELETE":
                return handle_delete_route(event)

        # Search
        if path == "/search" and method == "POST":
            return handle_search(event)

        # Favorites
        if path == "/favorites" and method == "POST":
            return handle_add_favorite(event)
        if path == "/favorites" and method == "GET":
            return handle_get_favorites(event)
        if re.match(r"^/favorites/[\w-]+$", path):
            if method == "DELETE":
                return handle_delete_favorite(event)

        # Dashboard
        if path == "/dashboard" and method == "GET":
            return handle_dashboard(event)

        # Notifications
        if path == "/subscribe" and method == "POST":
            return handle_subscribe(event)
        if path == "/subscribers" and method == "GET":
            return handle_get_subscribers(event)

        return json_response(404, {"error": f"Route not found: {method} {path}"})

    except Exception as e:
        return json_response(500, {"error": f"Internal server error: {str(e)}"})
