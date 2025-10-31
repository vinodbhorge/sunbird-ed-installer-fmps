#!/usr/bin/env python3
import requests

USER_ID = "{{ .Values.user_id }}"

KEYCLOAK_TOKEN_URL = f"{{ .Values.baseUrl }}/auth/realms/sunbird/protocol/openid-connect/token"
REFRESH_URL = f"{{ .Values.baseUrl }}/auth/v1/refresh/token"
BATCH_LIST_URL = f"{{ .Values.baseUrl }}/api/course/v1/batch/list"
SUBMIT_URL = f"{{ .Values.request_submit_url }}/request/submit"
SEARCH_URL = f"{{ .Values.search_url }}/v3/search"
CHANNEL_ID_URL = f"{{ .Values.baseUrl }}/api/org/v1/search"

CLIENT_ID = "{{ .Values.client_id }}"
CLIENT_SECRET = "{{ .Values.client_secret }}"
USERNAME = "{{ .Values.username }}"
PASSWORD = "{{ .Values.password }}"

API_KEY = "{{ .Values.api_key }}"
# -----------------------------


def search_courses(channel_id):
    payload = {
        "request": {
            "filters": {
                "primaryCategory": ["Course"],
                "status": ["Live"]
            },
            "limit": 1000,
            "sort_by": {"lastPublishedOn": "desc"},
            "fields": ["name", "identifier"]
        }
    }
    headers = {"Content-Type": "application/json", "X-Channel-Id": channel_id}
    resp = requests.post(SEARCH_URL, json=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    identifiers = [c["identifier"] for c in data.get("result", {}).get("content", [])]
    print(f"Search returned {identifiers} courses")
    return identifiers


def get_access_token():
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(KEYCLOAK_TOKEN_URL, data=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    access = data.get("access_token")
    refresh = data.get("refresh_token")
    print(f"Access token: {access}")
    return access, refresh


def refresh_token(refresh_token_str):
    if not refresh_token_str:
        raise ValueError("No refresh token available to refresh the access token")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {"refresh_token": refresh_token_str}

    resp = requests.post(REFRESH_URL, data=payload, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    refreshed_access = None
    if isinstance(data, dict):
        refreshed_access = (
            data.get("access_token")
            or data.get("result", {}).get("access_token")
            or data.get("result", {}).get("accessToken")
        )
    print(f"Refreshed access token: {refreshed_access}")
    return refreshed_access


def get_root_org_id():
    org_name="FMPS"
    payload = {
        "request": {
            "filters": {"orgName": org_name},
            "fields": ["rootOrgId"]
        }
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(CHANNEL_ID_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        root_org_id = (
            data.get("result", {})
            .get("response", {})
            .get("content", [{}])[0]
            .get("rootOrgId")
        )
        print(f"rootOrgId for '{org_name}': {root_org_id}")
        return root_org_id
    except Exception as e:
        print(f"Failed to fetch rootOrgId for '{org_name}': {e}")
        return None


def get_batches(course_ids, token, api_key=None):
    if api_key is None:
        api_key = globals().get("API_KEY")

    single_mode = False
    # Accept a single string or an iterable of ids
    if isinstance(course_ids, str):
        single_mode = True
        ids = [course_ids]
    else:
        ids = list(course_ids)

    results = {}
    for cid in ids:
        payload = {
            "request": {
                "filters": {"courseId": cid, "status": [1]},
                "limit": 1000,
                "fields": ["name", "identifier", "batchId", "status"]
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-authenticated-user-token": token
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        else:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = requests.post(BATCH_LIST_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            batch_ids = [b.get("batchId") for b in data.get("result", {}).get("response", {}).get("content", []) if b.get("batchId")]
        except Exception as e:
            print(f"Warning: failed to fetch batches for course {cid}: {e}")
            batch_ids = []

        results[cid] = batch_ids
        print(f"Batch list for course {cid}: {batch_ids}")

    if single_mode:
        return results.get(ids[0], [])
    return results


def progress_exhaust_submit_request(batch_id, token, course_id, channel_id):
    payload = {
        "request": {
            "tag": f"{course_id}_{batch_id}",
            "requestedBy": USER_ID,
            "dataset": "progress-exhaust",
            "datasetConfig": {"batchId": batch_id},
            "output_format": "csv"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-Channel-Id": channel_id,
        "x-authenticated-userid": USER_ID,
        "x-authenticated-user-token": token
    }
    resp = requests.post(SUBMIT_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()

def response_exhaust_submit_request(batch_id, token, course_id, channel_id):
    payload = {
        "request": {
            "tag": f"{course_id}_{batch_id}",
            "requestedBy": USER_ID,
            "dataset": "response-exhaust",
            "datasetConfig": {"batchId": batch_id},
            "output_format": "csv"
        }
    }
    headers = {
        "Content-Type": "application/json",
        "X-Channel-Id": channel_id,
        "x-authenticated-userid": USER_ID,
        "x-authenticated-user-token": token
    }
    resp = requests.post(SUBMIT_URL, json=payload, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():

    channel_id = get_root_org_id()
    # Step 1: Search courses
    course_ids = search_courses(channel_id)
    print(f"Found {len(course_ids)} courses")

    # Step 2: Get token
    access_token, refresh_tok = get_access_token()
    print("Got access token")

    # Step 3: Refresh token using the refresh token value returned by keycloak
    if refresh_tok:
        token = refresh_token(refresh_tok)
        print("Got refreshed token")
    else:
        # fallback: if no refresh token was returned, continue with the access token
        token = access_token
        print("No refresh token returned by token endpoint; using access token as-is")

    # Step 4: Get batches for all courses (returns dict course_id -> [batchIds])
    course_batches = get_batches(course_ids, token, API_KEY)

    # Iterate through each course and submit requests for all its batches
    if isinstance(course_batches, dict):
        for course_id, batch_ids in course_batches.items():
            if not batch_ids:
                print(f"Course {course_id} has no batches; skipping submission")
                continue
            print(f"Course {course_id} has batches: {batch_ids}")
            for batch_id in batch_ids:
                resp_exhaust = response_exhaust_submit_request(batch_id, token, course_id, channel_id)
                progress_exhaust = progress_exhaust_submit_request(batch_id, token, course_id, channel_id)
                # print(resp_exhaust)
                print(progress_exhaust)
                # print(f"Submitted batch {batch_id}: {resp_exhaust}")
                print(f"Submitted batch {batch_id}: {progress_exhaust}")
    else:
        # Fallback: if a single list was returned, treat as single course's batch list
        for course_id in course_ids:
            batch_ids = course_batches
            if not batch_ids:
                print(f"Course {course_id} has no batches; skipping submission")
                continue
            print(f"Course {course_id} has batches: {batch_ids}")
            for batch_id in batch_ids:
                resp_exhaust = response_exhaust_submit_request(batch_id, token, course_id , channel_id)
                progress_exhaust = progress_exhaust_submit_request(batch_id, token, course_id, channel_id)
                # print(resp_exhaust)
                print(progress_exhaust)
                # print(f"Submitted batch {batch_id}: {resp_exhaust}")
                print(f"Submitted batch {batch_id}: {progress_exhaust}")


if __name__ == "__main__":
    main()