import pytest
from uuid import UUID
from unittest.mock import patch, MagicMock

@pytest.fixture
def create_wallet(async_client):
    def _create_wallet(balance: str = "0.00"):
        wallet_data = {"balance": balance}
        response = async_client.post(
            "/api/v1/wallets/", 
            json=wallet_data,
            )
        assert response.status_code == 200
        return response.json()
    return _create_wallet

@pytest.fixture
def perform_operation(async_client):
    def _perform_operation(wallet_id: UUID, operation_type: str, amount: str):
        operation_data = {
            "operation_type": operation_type,
            "amount": amount
        }
        return async_client.post(
            f"/api/v1/wallets/{wallet_id}/operation", 
            json=operation_data,
            )
    return _perform_operation

def test_get_nonexistent_wallet(async_client):
    non_existent_wallet_id = UUID(
        "00000000-0000-0000-0000-000000000000",
        )
    response = async_client.get(
        f"/api/v1/wallets/{non_existent_wallet_id}",
        )
    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"

def test_create_wallet(create_wallet):
    wallet = create_wallet()
    assert wallet["balance"] == "0.00"
    assert "id" in wallet

def test_get_wallet(async_client, create_wallet):
    wallet = create_wallet("100.00")
    response = async_client.get(
        f"/api/v1/wallets/{wallet["id"]}",
        )
    assert response.status_code == 200
    assert "balance" in response.json()

def test_create_deposit_operation(create_wallet, perform_operation):
    wallet = create_wallet("100.00")
    with patch("app.celery_app.celery_app.send_task") as mock_send_task:
        mock_task = MagicMock()
        mock_task.id = "fake_task_id"
        mock_send_task.return_value = mock_task
        response = perform_operation(
            wallet["id"], "DEPOSIT", "50.00",
            )
        assert response.status_code == 200
        assert response.json()["task_id"] == "fake_task_id"

def test_create_withdraw_operation(create_wallet, perform_operation):
    wallet = create_wallet("100.00")
    with patch("app.celery_app.celery_app.send_task") as mock_send_task:
        mock_task = MagicMock()
        mock_task.id = "fake_task_id"
        mock_send_task.return_value = mock_task
        response = perform_operation(
            wallet["id"], "WITHDRAW", "50.00",
            )
        assert response.status_code == 200
        assert response.json()["task_id"] == "fake_task_id"

def test_create_withdraw_operation_insufficient_funds(create_wallet, perform_operation):
    wallet = create_wallet("100.00")
    response = perform_operation(
        wallet["id"], "WITHDRAW", "150.00",
        )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

def test_create_wallet_with_negative_balance_fails(async_client):
    wallet_data = {"balance": "-100.00"}
    response = async_client.post(
        "/api/v1/wallets/", 
        json=wallet_data,
        )
    error_msg = "Input should be greater than or equal to 0.0"
    assert error_msg == response.json()["detail"][0]["msg"]