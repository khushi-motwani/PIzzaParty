from unittest.mock import Mock, patch
from dao.transactions_dao import TransactionsDao


@patch('dao.transactions_dao.get_db_connection')
def test_count_transactions(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [(10,)]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.count()

    assert result == 10
    assert dao.total == 10


@patch('dao.transactions_dao.get_db_connection')
def test_get_all_transactions(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        (1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00),
        (2, 1, 2, "SELL", 5, 250.00, "2024-01-20", 1250.00, 49750.00)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.get_all()

    assert len(result) == 2
    assert result[0].transaction_type == "BUY"
    assert result[1].transaction_type == "SELL"


@patch('dao.transactions_dao.get_db_connection')
def test_get_all_empty_table(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.get_all()

    assert result == []
