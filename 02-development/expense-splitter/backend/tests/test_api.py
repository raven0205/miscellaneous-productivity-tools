import pytest
from fastapi.testclient import TestClient

from app.main import app, create_app_state


@pytest.fixture
def client():
    original_state = app.state.app_state
    app.state.app_state = create_app_state(database_url='sqlite://')

    with TestClient(app) as test_client:
        yield test_client

    app.state.app_state = original_state


def test_get_groups_returns_initial_group_data(client):
    response = client.get('/api/groups')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "group-trip"
    assert data[0]["name"] == "Weekend Trip"
    assert len(data[0]["members"]) == 3
    assert len(data[0]["expenses"]) == 2


def test_create_group_success(client):
    response = client.post('/api/groups', json={"name": "Birthday Trip"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Birthday Trip"
    assert data["id"]
    assert data["members"] == []
    assert data["expenses"] == []


def test_create_group_rejects_empty_name(client):
    response = client.post('/api/groups', json={"name": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Group name is required."


def test_add_member_success(client):
    response = client.post('/api/groups/group-trip/members', json={"name": "Dana"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Dana"
    assert data["id"]

    groups_response = client.get('/api/groups')
    assert any(member["name"] == "Dana" for member in groups_response.json()[0]["members"])


def test_add_member_unknown_group(client):
    response = client.post('/api/groups/unknown-group/members', json={"name": "Dana"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found."


def test_add_member_rejects_empty_name(client):
    response = client.post('/api/groups/group-trip/members', json={"name": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Member name is required."


def test_add_member_rejects_duplicate_name(client):
    response = client.post('/api/groups/group-trip/members', json={"name": "Alice"})

    assert response.status_code == 400
    assert response.json()["detail"] == "A participant with that name already exists."


def test_create_expense_success(client):
    response = client.post(
        '/api/groups/group-trip/expenses',
        json={
            "description": "Taxi ride",
            "total_amount": 120,
            "payer_id": "member-alice",
            "splits": [
                {"member_id": "member-alice", "amount": 60},
                {"member_id": "member-ben", "amount": 30},
                {"member_id": "member-chloe", "amount": 30},
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Taxi ride"
    assert data["total_amount"] == 120
    assert data["payer_id"] == "member-alice"
    assert len(data["splits"]) == 3


def test_create_expense_unknown_group(client):
    response = client.post(
        '/api/groups/unknown-group/expenses',
        json={
            "description": "Taxi ride",
            "total_amount": 120,
            "payer_id": "member-alice",
            "splits": [{"member_id": "member-alice", "amount": 120}],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found."


def test_create_expense_rejects_empty_group_members(client):
    created_group = client.post('/api/groups', json={"name": "Empty Group"})
    group_id = created_group.json()["id"]

    response = client.post(
        f'/api/groups/{group_id}/expenses',
        json={
            "description": "Taxi ride",
            "total_amount": 120,
            "payer_id": "member-alice",
            "splits": [],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Add at least one participant before logging an expense."


def test_parse_receipt_success(client):
    response = client.post(
        '/api/ai/parse-receipt',
        json={"receipt_text": "Dinner total: $80.00\nThanks for visiting!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Thanks for visiting!"
    assert data["total_amount"] == 80.0


def test_parse_receipt_rejects_empty_text(client):
    response = client.post('/api/ai/parse-receipt', json={"receipt_text": "   "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Paste a receipt text first."
