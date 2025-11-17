from flask import request, jsonify
from database import get_supabase

MIN_TAG_LENGTH = 2
MAX_TAG_LENGTH = 20

def add_tag_to_poll():
    """Add a tag to a poll
    
    Expected JSON payload:
    {
        "tag": "Tag name"
        "ID": "Poll ID"
    }
    """
    try:
        data = request.get_json()

        #Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        tag = data.get("tag", "").strip()
        ID = data.get("ID", "").strip()
        
        try:
            ID = int(ID)
        except (ValueError, TypeError):
            return jsonify({"error": "Poll ID must be a valid integer"}), 400
        
        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        response = supabase.table("tags").select("id").eq("name", tag).execute()

        if response.error:
            return jsonify({"error": f"Database error: {response.error.message}"}), 503

        if len(response.data) == 0:
            #Create tag if doesn't already exist

            #Validate tag name
            if(len(tag) < MIN_TAG_LENGTH):
                return jsonify({"error": f"Tag must be at least {MIN_TAG_LENGTH} characters"}), 400
            
            if(len(tag) > MAX_TAG_LENGTH):
                return jsonify({"error": f"Tag must not exceed {MAX_TAG_LENGTH} characters"}), 400
            
            #Add tag to database
            tagID = create_tag(tag)
            if not tagID:
                return jsonify({"error": "Failed to create tag"}), 500
        else:
            tagID = response.data[0]["id"]

        #Create poll-tag relation in database
        poll_tags_data = {
            "poll_id": ID,
            "tag_id": tagID
        }

        result = supabase.table("poll_tags").insert(poll_tags_data).execute()

        if not result.data:
            return jsonify({"error": "Failed to create poll"}), 500

        return jsonify({
            "message": "Tag added successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def create_tag(name: str) -> int:
    supabase = get_supabase()

    if not supabase:
        return None
    
    tag_data = { "name": name}
    
    result = supabase.table("tags").insert(tag_data).execute()

    if not result.data:
        return None

    return result.data[0]["id"]

def get_all_tags():
    """Return all tags which contain the substring match. Passing an empty string as match returns all tags
    
    Expected JSON payload:
    {
        "match": "String to match with tag"
    }
    """
    try:
        data = request.get_json()

        #Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        #Pass is match = "" to return all tags, regardless of name
        match = data.get("match", "").strip()

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        search_pattern = f"%{match}%"
        
        response = supabase.table("tags").select("*").ilike("name", search_pattern).execute()

        if not response:
            return jsonify("error", "Failed to retrieve tags"), 500
        
        return jsonify({
            "message": "Successfully retrieved tags",
            "tags": response.data
        }), 200

        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def get_tag_by_id():
    """Return the tag which matches the provided ID
    
    Expected JSON payload:
    {
        "id": 12345678
    }"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        id = data.get("id", "").strip()

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503
        
        search_pattern = f"%{id}%"

        response = supabase.table("tags").select("*").ilike("name", search_pattern).execute()

        if not response:
            return jsonify("error", "Failed to retrieve tag"), 500
        
        return jsonify({
            "message": "Successfully retrieved tag",
            "tag": response.data[0]
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500