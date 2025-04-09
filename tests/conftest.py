import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "POCKETBASE_URL": "http://test-pb:8090"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def mock_pb(mocker):
    """Mock PocketBase service."""
    mock = mocker.patch('app.services.pocketbase_service.PocketBaseService')
    mock.return_value.authenticate.return_value = True
    mock.return_value.tenant_id_exists.return_value = False
    return mock