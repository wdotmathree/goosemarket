from flask import request, jsonify, make_response
from base64 import b64decode, b64encode
from dotenv import load_dotenv
from json import loads, dumps
from typing import Optional
import supabase as sb
import jwt
import os

from database import get_supabase

load_dotenv()
jwks = jwt.PyJWKClient(os.getenv("SUPABASE_URL") + "/auth/v1/.well-known/jwks.json")

def _validate_token(token):
	try:
		signing_key = jwks.get_signing_key_from_jwt(token)
		jwt.decode(token, signing_key.key, algorithms=["ES256", "RS256"], options={"verify_exp": True, "verify_aud": False})
		return True
	except Exception as e:
		raise e
		return False

def verify_token(token: str) -> Optional[str]:
	"""
	Verifies a JWT token and tries to regenerate it if expired.
	- If the current token is valid, returns (token, None).
	- If the token was expired but successfully refreshed, returns (new_token, refresh_token, expires_at).
	- If the token is invalid and cannot be refreshed, returns None.
	"""
	if not token:
		return None
	if _validate_token(token):
		return token, None
	# Try to refresh token
	supabase = get_supabase()
	try:
		res = supabase.auth.refresh_session(token)
	except Exception:
		return None
	if not res.session:
		return None
	# Check if new token is valid
	if _validate_token(res.session.access_token):
		return res.session.access_token, res.session.refresh_token, res.session.expires_at
	return None


def login():
	# Get info from request
	data = request.get_json()
	email = data.get("email")
	password = data.get("password")

	# Authenticate with Supabase
	supabase = get_supabase()
	try:
		res = supabase.auth.sign_in_with_password({
			"email": email,
			"password": password
		})
	except sb.AuthError as e:
		return jsonify({"error": str(e)}), 400
	except Exception as e:
		return jsonify({"error": str(e), "type": str(type(e))}), 500
	# Did not work 🥀
	if not res.user:
		return jsonify({"error": "Invalid login credentials"}), 401

	# Get other info
	try:
		username, admin = supabase.table("profiles").select("username", "admin").eq("auth_id", res.user.id).execute().data[0].values()
	except Exception as e:
		return jsonify({"error": "Failed to retrieve user profile: " + str(e)}), 500

	# Send everything back
	token_data = res.session
	res = make_response()
	res.set_cookie("sb-access-token", token_data.access_token, expires=token_data.expires_at, httponly=True)
	res.set_cookie("sb-refresh-token", token_data.refresh_token, httponly=True)
	res.set_cookie("user-info", b64encode(dumps({"username": username, "email": email, "admin": admin}).encode()).decode(), expires=token_data.expires_at)
	return res, 200


def register():
	# Get and validate info from request
	data = request.get_json()
	email = data.get("email")
	password = data.get("password")
	username = data.get("username")
	# Email has to end with @uwaterloo.ca and not have + (to prevent aliasing)
	if "+" in email or not email.endswith("@uwaterloo.ca"):
		return jsonify({"error": "Invalid email address"}), 400
	# Password required
	if not password:
		return jsonify({"error": "Password is required"}), 400
	# Username default if they dont include one
	if not username:
		username = email.split("@")[0]

	# Check if stuff is taken
	supabase = get_supabase()
	try:
		res = supabase.table("profiles").select("email").eq("email", email).execute()
	except Exception as e:
		return jsonify({"error": "Failed to check email availability: " + str(e)}), 500
	if res.data and len(res.data) > 0:
		return jsonify({"error": "Email is already registered"}), 400

	try:
		res = supabase.table("profiles").select("username").eq("username", username).execute()
	except Exception as e:
		return jsonify({"error": "Failed to check username availability: " + str(e)}), 500
	if res.data and len(res.data) > 0:
		return jsonify({"error": "Username is already taken"}), 400

	# Make account
	try:
		res = supabase.auth.sign_up({
			"email": email,
			"password": password,
			"options": {
				"email_redirect_to": request.headers.get("Origin") + "/login"
			}
		})
	except Exception as e:
		return jsonify({"error": str(e), "type": type(e)}), 500

	# Something weird happened but wasn't reported earlier somehow
	if not res.user:
		return jsonify({"error": "Registration failed"}), 400

	# Create profile in db
	try:
		supabase.table("profiles").insert({
			"auth_id": res.user.id,
			"username": username,
			"email": email
		}).execute()
	except Exception as e:
		return jsonify({"error": "Failed to create user profile: " + str(e)}), 500

	return "", 200


# Handles email verification callback
def verify_email():
	# Get info from request
	data = request.get_json()
	token = data.get("access_token")
	if not token:
		return jsonify({"error": "Token is required"}), 400
	if not "expires_at" in data:
		return jsonify({"error": "Invalid token data"}), 400

	# We only care about the info part of the JWT
	padded = token.split(".")[1] + "=="
	email = loads(b64decode(padded).decode()).get("email")

	# Get user profile and send cookies
	supabase = get_supabase()
	try:
		username, admin = supabase.table("profiles").select("username", "admin").eq("email", email).execute().data[0].values()
	except Exception as e:
		return jsonify({"error": "Failed to retrieve user profile: " + str(e)}), 500

	res = make_response()
	res.set_cookie("sb-access-token", token, expires=data.get("expires_at"), httponly=True)
	res.set_cookie("sb-refresh-token", data.get("refresh_token"), httponly=True)
	res.set_cookie("user-info", b64encode(dumps({"username": username, "email": email, "admin": admin}).encode()).decode(), expires=data.get("expires_at"))

	return res, 200
