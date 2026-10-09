from fastapi.testclient import TestClient

from app.main import app
from app.utils.jwt import create_access_token


client = TestClient(app)

TENANT_A = "tenant-a"
TENANT_B = "tenant-b"


def auth_headers(tenant_id: str) -> dict[str, str]:
    token = create_access_token(
        {
            "sub": f"test-user-{tenant_id}",
            "tenant_id": tenant_id,
        }
    )

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/scim+json",
    }


TENANT_A_HEADERS = auth_headers(TENANT_A)
TENANT_B_HEADERS = auth_headers(TENANT_B)


def assert_scim_error(response, status_code: int) -> None:
    assert response.status_code == status_code

    body = response.json()

    assert body["schemas"] == [
        "urn:ietf:params:scim:api:messages:2.0:Error"
    ]
    assert isinstance(body["detail"], str)
    assert body["detail"]
    assert body["status"] == str(status_code)


def create_user(
    username: str = "test@example.com",
    headers: dict | None = None,
):
    response = client.post(
        "/scim/v2/Users",
        headers=headers or TENANT_A_HEADERS,
        json={
            "userName": username,
            "active": True,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["userName"] == username

    return body


def create_group(
    display_name: str = "Engineering",
    headers: dict | None = None,
):
    response = client.post(
        "/scim/v2/Groups",
        headers=headers or TENANT_A_HEADERS,
        json={
            "displayName": display_name,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["displayName"] == display_name

    return body


# ============================================================================
# USER API
# ============================================================================


def test_create_user_api():
    response = client.post(
        "/scim/v2/Users",
        headers=TENANT_A_HEADERS,
        json={
            "userName": "gunavardhan@example.com",
            "active": True,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["userName"] == "gunavardhan@example.com"
    assert body["active"] is True
    assert "schemas" in body


def test_list_users_api():
    create_user(
        "list-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.get(
        "/scim/v2/Users",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["schemas"] == [
        "urn:ietf:params:scim:api:messages:2.0:ListResponse"
    ]
    assert "total_results" in body
    assert "start_index" in body
    assert "items_per_page" in body
    assert "resources" in body
    assert body["total_results"] >= 1


def test_get_user_api():
    user = create_user(
        "get-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.get(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user["id"]
    assert body["userName"] == "get-user@example.com"


def test_replace_user_api():
    user = create_user(
        "old-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.put(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "userName": "new-user@example.com",
            "active": True,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user["id"]
    assert body["userName"] == "new-user@example.com"


def test_patch_user_api():
    user = create_user(
        "patch-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "active",
                    "value": False,
                }
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user["id"]
    assert body["active"] is False


def test_delete_user_api():
    user = create_user(
        "delete-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.delete(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 204

    response = client.get(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert_scim_error(response, 404)


# ============================================================================
# GROUP API
# ============================================================================


def test_create_group_api():
    response = client.post(
        "/scim/v2/Groups",
        headers=TENANT_A_HEADERS,
        json={
            "displayName": "Engineering",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["displayName"] == "Engineering"
    assert "schemas" in body


def test_list_groups_api():
    create_group(
        "Security",
        TENANT_A_HEADERS,
    )

    response = client.get(
        "/scim/v2/Groups",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["schemas"] == [
        "urn:ietf:params:scim:api:messages:2.0:ListResponse"
    ]
    assert "total_results" in body
    assert "start_index" in body
    assert "items_per_page" in body
    assert "resources" in body
    assert body["total_results"] >= 1


def test_get_group_api():
    group = create_group(
        "Get Engineering",
        TENANT_A_HEADERS,
    )

    response = client.get(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == group["id"]
    assert body["displayName"] == "Get Engineering"


def test_replace_group_api():
    group = create_group(
        "Old Engineering",
        TENANT_A_HEADERS,
    )

    response = client.put(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "displayName": "New Engineering",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == group["id"]
    assert body["displayName"] == "New Engineering"


def test_patch_group_api():
    group = create_group(
        "Old Security",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "displayName",
                    "value": "New Security",
                }
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == group["id"]
    assert body["displayName"] == "New Security"


def test_delete_group_api():
    group = create_group(
        "Temporary Group",
        TENANT_A_HEADERS,
    )

    response = client.delete(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert response.status_code == 204

    response = client.get(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
    )

    assert_scim_error(response, 404)


# ============================================================================
# AUTHENTICATION / TENANT CONTEXT
# ============================================================================


def test_user_requires_authentication():
    response = client.get("/scim/v2/Users")

    assert response.status_code in (401, 403)


def test_group_requires_authentication():
    response = client.get("/scim/v2/Groups")

    assert response.status_code in (401, 403)


def test_user_requires_tenant_claim():
    token = create_access_token(
        {
            "sub": "test-user-without-tenant",
        }
    )

    response = client.get(
        "/scim/v2/Users",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401


def test_group_requires_tenant_claim():
    token = create_access_token(
        {
            "sub": "test-user-without-tenant",
        }
    )

    response = client.get(
        "/scim/v2/Groups",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 401


# ============================================================================
# CROSS-TENANT ISOLATION
# ============================================================================


def test_user_cross_tenant_get():
    user = create_user(
        "tenant-a-user@example.com",
        TENANT_A_HEADERS,
    )

    response = client.get(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_B_HEADERS,
    )

    assert_scim_error(response, 404)


def test_user_cross_tenant_put():
    user = create_user(
        "tenant-a-put@example.com",
        TENANT_A_HEADERS,
    )

    response = client.put(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_B_HEADERS,
        json={
            "userName": "attacker@example.com",
            "active": True,
        },
    )

    assert_scim_error(response, 404)


def test_user_cross_tenant_patch():
    user = create_user(
        "tenant-a-patch@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_B_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "active",
                    "value": False,
                }
            ],
        },
    )

    assert_scim_error(response, 404)


def test_user_cross_tenant_delete():
    user = create_user(
        "tenant-a-delete@example.com",
        TENANT_A_HEADERS,
    )

    response = client.delete(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_B_HEADERS,
    )

    assert_scim_error(response, 404)


def test_group_cross_tenant_get():
    group = create_group(
        "Tenant A Group",
        TENANT_A_HEADERS,
    )

    response = client.get(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_B_HEADERS,
    )

    assert_scim_error(response, 404)


def test_group_cross_tenant_put():
    group = create_group(
        "Tenant A Put Group",
        TENANT_A_HEADERS,
    )

    response = client.put(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_B_HEADERS,
        json={
            "displayName": "Unauthorized Update",
        },
    )

    assert_scim_error(response, 404)


def test_group_cross_tenant_patch():
    group = create_group(
        "Tenant A Patch Group",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_B_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "displayName",
                    "value": "Unauthorized Update",
                }
            ],
        },
    )

    assert_scim_error(response, 404)


def test_group_cross_tenant_delete():
    group = create_group(
        "Tenant A Delete Group",
        TENANT_A_HEADERS,
    )

    response = client.delete(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_B_HEADERS,
    )

    assert_scim_error(response, 404)


# ============================================================================
# NOT FOUND
# ============================================================================


def test_user_not_found():
    response = client.get(
        "/scim/v2/Users/non-existent-user",
        headers=TENANT_A_HEADERS,
    )

    assert_scim_error(response, 404)


def test_group_not_found():
    response = client.get(
        "/scim/v2/Groups/non-existent-group",
        headers=TENANT_A_HEADERS,
    )

    assert_scim_error(response, 404)


# ============================================================================
# PATCH VALIDATION
# ============================================================================


def test_user_patch_invalid_operation():
    user = create_user(
        "invalid-operation@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "invalid",
                    "path": "active",
                    "value": False,
                }
            ],
        },
    )

    assert_scim_error(response, 400)


def test_user_patch_invalid_path():
    user = create_user(
        "invalid-path@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "unsupportedAttribute",
                    "value": "test",
                }
            ],
        },
    )

    assert_scim_error(response, 400)


def test_user_patch_missing_value():
    user = create_user(
        "missing-value@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "active",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert_scim_error(response, 400)


def test_user_patch_remove_with_value():
    user = create_user(
        "remove-with-value@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "remove",
                    "path": "active",
                    "value": True,
                }
            ],
        },
    )

    assert_scim_error(response, 400)


def test_user_patch_wrong_active_type():
    user = create_user(
        "wrong-active-type@example.com",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Users/{user['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "active",
                    "value": "false",
                }
            ],
        },
    )

    assert_scim_error(response, 400)


def test_group_patch_invalid_operation():
    group = create_group(
        "Invalid Operation Group",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "invalid",
                    "path": "displayName",
                    "value": "Test",
                }
            ],
        },
    )

    assert_scim_error(response, 400)


def test_group_patch_invalid_path():
    group = create_group(
        "Invalid Path Group",
        TENANT_A_HEADERS,
    )

    response = client.patch(
        f"/scim/v2/Groups/{group['id']}",
        headers=TENANT_A_HEADERS,
        json={
            "schemas": [
                "urn:ietf:params:scim:api:messages:2.0:PatchOp"
            ],
            "Operations": [
                {
                    "op": "replace",
                    "path": "unsupportedAttribute",
                    "value": "Test",
                }
            ],
        },
    )

    assert_scim_error(response, 400)


# ============================================================================
# REQUEST VALIDATION
# ============================================================================

# FastAPI/Pydantic request-model validation occurs before the SCIM
# router executes, so malformed request bodies return HTTP 422.
# Router/service validation errors use the SCIM Error response contract.


def test_create_user_invalid_request():
    response = client.post(
        "/scim/v2/Users",
        headers=TENANT_A_HEADERS,
        json={
            "active": True,
        },
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_create_group_invalid_request():
    response = client.post(
        "/scim/v2/Groups",
        headers=TENANT_A_HEADERS,
        json={},
    )

    assert response.status_code == 422
    assert "detail" in response.json()


def test_scim_openapi_exposes_all_12_routes():
    from app.main import app

    expected_routes = {
        ("GET", "/scim/v2/Users"),
        ("POST", "/scim/v2/Users"),
        ("GET", "/scim/v2/Users/{user_id}"),
        ("PUT", "/scim/v2/Users/{user_id}"),
        ("PATCH", "/scim/v2/Users/{user_id}"),
        ("DELETE", "/scim/v2/Users/{user_id}"),
        ("GET", "/scim/v2/Groups"),
        ("POST", "/scim/v2/Groups"),
        ("GET", "/scim/v2/Groups/{group_id}"),
        ("PUT", "/scim/v2/Groups/{group_id}"),
        ("PATCH", "/scim/v2/Groups/{group_id}"),
        ("DELETE", "/scim/v2/Groups/{group_id}"),
    }

    openapi_routes = {
        (method.upper(), path)
        for path, methods in app.openapi()["paths"].items()
        if path.startswith("/scim/v2/")
        for method in methods
        if method.lower()
        in {
            "get",
            "post",
            "put",
            "patch",
            "delete",
        }
    }

    assert openapi_routes == expected_routes
