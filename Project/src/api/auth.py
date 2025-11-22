from flask import request, jsonify, make_response
from base64 import b64decode, b64encode
from json import loads, dumps

from database import get_supabase

import supabase as sb

def login():
	data = request.get_json()
	email = data.get("email")
	password = data.get("password")

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

	if not res.user:
		return jsonify({"error": "Invalid login credentials"}), 401
	
	try:
		username = supabase.table("profiles").select("username").eq("auth_id", res.user.id).execute().data[0]["username"]
	except Exception as e:
		return jsonify({"error": "Failed to retrieve user profile: " + str(e)}), 500

	token_data = res.session
	res = make_response()
	res.set_cookie("sb-access-token", token_data.access_token, expires=token_data.expires_at, httponly=True)
	res.set_cookie("sb-refresh-token", token_data.refresh_token, expires=token_data.expires_at, httponly=True)
	res.set_cookie("user-info", b64encode(dumps({"username": username, "email": email}).encode()).decode(), expires=token_data.expires_at)
	return res, 200


def register():
	data = request.get_json()
	email = data.get("email")
	password = data.get("password")
	username = data.get("username")
	if "+" in email or not email.endswith("@uwaterloo.ca"):
		return jsonify({"error": "Invalid email address"}), 400
	if not password:
		return jsonify({"error": "Password is required"}), 400
	if not username:
		username = email.split("@")[0]

	supabase = get_supabase()

	try:
		res = supabase.table("profiles").select("username").eq("username", username).execute()
	except Exception as e:
		return jsonify({"error": "Failed to check username availability: " + str(e)}), 500
	if res.data and len(res.data) > 0:
		return jsonify({"error": "Username is already taken"}), 400

	try:
		res = supabase.table("profiles").select("email").eq("email", email).execute()
	except Exception as e:
		return jsonify({"error": "Failed to check email availability: " + str(e)}), 500
	if res.data and len(res.data) > 0:
		return jsonify({"error": "Email is already registered"}), 400

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

	print(res.user.id)

	if not res.user:
		return jsonify({"error": "Registration failed"}), 400

	try:
		supabase.table("profiles").insert({
			"auth_id": res.user.id,
			"username": username,
			"email": email
		}).execute()
	except Exception as e:
		return jsonify({"error": "Failed to create user profile: " + str(e)}), 500

	return "", 200


def verify_email():
	data = request.get_json()
	token = data.get("access_token")
	if not token:
		return jsonify({"error": "Token is required"}), 400
	if not "expires_at" in data:
		return jsonify({"error": "Invalid token data"}), 400

	padded = token.split(".")[1]
	padded += "=" * (4 - len(padded) % 4)
	email = loads(b64decode(padded).decode()).get("email")

	supabase = get_supabase()
	try:
		username = supabase.table("profiles").select("username").eq("email", email).execute().data[0]["username"]
	except Exception as e:
		return jsonify({"error": "Failed to retrieve user profile: " + str(e)}), 500

	res = make_response()
	res.set_cookie("sb-access-token", token, expires=data.get("expires_at"), httponly=True)
	res.set_cookie("sb-refresh-token", data.get("refresh_token"), expires=data.get("expires_at"), httponly=True)
	res.set_cookie("user-info", b64encode(dumps({"username": username, "email": email}).encode()).decode(), expires=data.get("expires_at"))

	return res, 200
