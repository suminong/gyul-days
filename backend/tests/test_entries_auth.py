
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app
from app.security import create_access_token


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_data(db_session):
    user_a = models.User(
        username="testuser_a",
        email="test_a@example.com",
        password_hash="test_hash",
    )

    user_b = models.User(
        username="testuser_b",
        email="test_b@example.com",
        password_hash="test_hash",
    )

    db_session.add_all([user_a, user_b])
    db_session.commit()

    db_session.refresh(user_a)
    db_session.refresh(user_b)

    entry_a = models.Entry(
        content="User A private journal",
        author_id=user_a.id,
    )

    entry_b = models.Entry(
        content="User B private journal",
        author_id=user_b.id,
    )

    db_session.add_all([entry_a, entry_b])
    db_session.commit()

    db_session.refresh(entry_a)
    db_session.refresh(entry_b)

    return {
        "user_a": user_a,
        "user_b": user_b,
        "entry_a": entry_a,
        "entry_b": entry_b,
        "token_a": create_access_token(user_a.id),
        "token_b": create_access_token(user_b.id),
    }


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_user_cannot_view_entry(client, test_data):
    response = client.get(
        f"/entries/{test_data['entry_a'].id}"
    )

    assert response.status_code == 401


def test_unauthenticated_user_cannot_update_entry(client, test_data):
    response = client.patch(
        f"/entries/{test_data['entry_a'].id}",
        json={"content": "Unauthorized update"},
    )

    assert response.status_code == 401


def test_user_cannot_view_another_users_entry(client, test_data):
    response = client.get(
        f"/entries/{test_data['entry_a'].id}",
        headers=auth_header(test_data["token_b"]),
    )

    assert response.status_code == 403


def test_user_cannot_update_another_users_entry(client, test_data, db_session):
    response = client.patch(
        f"/entries/{test_data['entry_a'].id}",
        headers=auth_header(test_data["token_b"]),
        json={"content": "Unauthorized update"},
    )

    assert response.status_code == 403

    db_session.refresh(test_data["entry_a"])
    assert test_data["entry_a"].content == "User A private journal"


def test_user_can_view_own_entry(client, test_data):
    response = client.get(
        f"/entries/{test_data['entry_a'].id}",
        headers=auth_header(test_data["token_a"]),
    )

    assert response.status_code == 200
    assert response.json()["content"] == "User A private journal"


def test_user_can_update_own_entry(client, test_data):
    response = client.patch(
        f"/entries/{test_data['entry_a'].id}",
        headers=auth_header(test_data["token_a"]),
        json={"content": "Updated private journal"},
    )

    assert response.status_code == 200
    assert response.json()["content"] == "Updated private journal"

def test_unauthenticated_user_cannot_create_entry(client):
    response = client.post(
        "/entries",
        json={"content": "Unauthorized entry"},
    )
    assert response.status_code == 401

def test_user_can_create_own_entry(client, test_data):
    response = client.post(
        "/entries",
        headers=auth_header(test_data["token_a"]),
        json={"content": "New private journal"},
    )

    assert response.status_code == 201
    assert response.json()["content"] == "New private journal"
    assert response.json()["author"]["id"] == test_data["user_a"].id

def test_user_only_sees_own_entries(client, test_data):
    response = client.get(
        "/entries",
        headers=auth_header(test_data["token_a"]),
    )

    assert response.status_code == 200

    entries = response.json()
    entry_ids = [entry["id"] for entry in entries]

    assert test_data["entry_a"].id in entry_ids
    assert test_data["entry_b"].id not in entry_ids

def test_unauthenticated_user_cannot_list_entries(client):
    response = client.get("/entries")

    assert response.status_code == 401

def test_unauthenticated_user_cannot_delete_entry(client, test_data):
    response = client.delete(
        f"/entries/{test_data['entry_a'].id}"
    )

    assert response.status_code == 401

def test_user_cannot_delete_another_users_entry(client, test_data, db_session):
    entry_a = test_data["entry_a"]

    response = client.delete(
        f"/entries/{entry_a.id}",
        headers=auth_header(test_data["token_b"]),
    )

    assert response.status_code == 403

    db_session.expire_all()
    saved_entry = db_session.get(models.Entry, entry_a.id)

    assert saved_entry is not None
    assert saved_entry.content == "User A private journal"

def test_user_can_delete_own_entry(client, test_data, db_session):
    entry_id = test_data["entry_a"].id

    response = client.delete(
        f"/entries/{entry_id}",
        headers=auth_header(test_data["token_a"]),
    )

    assert response.status_code == 204

    db_session.expire_all()
    deleted_entry = db_session.get(models.Entry, entry_id)

    assert deleted_entry is None

def test_fake_image_upload_is_rejected(client, test_data, db_session):
    user_a = test_data["user_a"]

    space = models.Space(name="Test Space")
    db_session.add(space)
    db_session.flush()

    membership = models.SpaceMember(
        space_id=space.id,
        user_id=user_a.id,
        role="owner",
    )

    entry = models.Entry(
        content="Image upload test",
        author_id=user_a.id,
        space_id=space.id,
    )

    db_session.add_all([membership, entry])
    db_session.commit()

    response = client.post(
        f"/spaces/{space.id}/entries/{entry.id}/images",
        headers=auth_header(test_data["token_a"]),
        files={
            "file": (
                "fake.png",
                b"not a real image",
                "image/png",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image file"

def test_non_author_cannot_request_ai_tags(client, test_data, db_session):
    space = models.Space(name="AI Security Test")
    db_session.add(space)
    db_session.flush()

    db_session.add_all([
        models.SpaceMember(
            space_id=space.id,
            user_id=test_data["user_a"].id,
            role="owner",
        ),
        models.SpaceMember(
            space_id=space.id,
            user_id=test_data["user_b"].id,
            role="member",
        ),
    ])

    entry = models.Entry(
        content="User A private journal",
        author_id=test_data["user_a"].id,
        space_id=space.id,
    )

    db_session.add(entry)
    db_session.commit()

    response = client.post(
        f"/spaces/{space.id}/entries/{entry.id}/tag-suggestions",
        headers=auth_header(test_data["token_b"]),
    )

    assert response.status_code == 403