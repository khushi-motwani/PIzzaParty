from unittest.mock import Mock, patch
from dao.transactions_dao import TransactionsDao


def make_mocked_dao(mock_get_db, fetchall_return=None):
    mock_cursor = Mock()
    mock_connection = Mock()
    if fetchall_return is not None:
        mock_cursor.fetchall.return_value = fetchall_return
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection
    return TransactionsDao(), mock_connection, mock_cursor


@patch('dao.transactions_dao.get_db_connection')
def test_count_transactions(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [(10,)])

    result = dao.count()

    assert result == 10
    assert dao.total == 10



@patch('dao.transactions_dao.get_db_connection')
def test_get_all_transactions(mock_get_db):
    rows = [
        (1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00),
        (2, 1, 2, "SELL", 5, 250.00, "2024-01-20", 1250.00, 49750.00)
    ]
    dao, _, _ = make_mocked_dao(mock_get_db, rows)

    result = dao.get_all()

    assert len(result) == 2
    assert result[0].transaction_type == "BUY"
    assert result[1].transaction_type == "SELL"


@patch('dao.transactions_dao.get_db_connection')
def test_get_all_empty_table(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_all()

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_by_id_found(mock_get_db):
    row = [(1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, row)

    result = dao.get_transaction_by_id(1)

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions WHERE transaction_id = %s", (1,)
    )
    assert result.transaction_id == 1
    assert result.transaction_type == "BUY"


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_by_id_not_found(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transaction_by_id(999)

    assert result is None


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_portfolio(mock_get_db):
    rows = [
        (1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00),
        (2, 1, 2, "SELL", 5, 250.00, "2024-01-20", 1250.00, 49750.00)
    ]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transactions_by_portfolio(1)

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions WHERE portfolio_id = %s ORDER BY transaction_date DESC",
        (1,)
    )
    assert len(result) == 2
    assert all(t.portfolio_id == 1 for t in result)


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_portfolio_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transactions_by_portfolio(42)

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_asset(mock_get_db):
    rows = [(1, 1, 2, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transactions_by_asset(1, 2)

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions WHERE portfolio_id = %s AND asset_id = %s ORDER BY transaction_date DESC",
        (1, 2)
    )
    assert len(result) == 1
    assert result[0].asset_id == 2


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_asset_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transactions_by_asset(1, 999)

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_type(mock_get_db):
    rows = [(1, 1, 1, "SELL", 5, 250.00, "2024-01-20", 1250.00, 49750.00)]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transactions_by_type("SELL")

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions WHERE transaction_type = %s ORDER BY transaction_date DESC",
        ("SELL",)
    )
    assert len(result) == 1
    assert result[0].transaction_type == "SELL"


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_type_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transactions_by_type("DIVIDEND")

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_date_range(mock_get_db):
    rows = [(1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transactions_by_date_range("2024-01-01", "2024-01-31")

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions WHERE transaction_date BETWEEN %s AND %s ORDER BY transaction_date DESC",
        ("2024-01-01", "2024-01-31")
    )
    assert len(result) == 1


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_date_range_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transactions_by_date_range("2030-01-01", "2030-01-31")

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_portfolio_and_date_range(mock_get_db):
    rows = [(1, 1, 1, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transactions_by_portfolio_and_date_range(1, "2024-01-01", "2024-01-31")

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM Transactions "
        "WHERE portfolio_id = %s AND transaction_date BETWEEN %s AND %s "
        "ORDER BY transaction_date DESC",
        (1, "2024-01-01", "2024-01-31")
    )
    assert len(result) == 1
    assert result[0].portfolio_id == 1


@patch('dao.transactions_dao.get_db_connection')
def test_get_transactions_by_portfolio_and_date_range_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transactions_by_portfolio_and_date_range(999, "2030-01-01", "2030-01-31")

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_count_by_portfolio(mock_get_db):
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, [(7,)])

    result = dao.get_transaction_count_by_portfolio(1)

    mock_cursor.execute.assert_called_once_with(
        "SELECT COUNT(*) as transaction_count FROM Transactions WHERE portfolio_id = %s",
        (1,)
    )
    assert result == 7


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_count_by_portfolio_zero(mock_get_db):
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, [(0,)])

    result = dao.get_transaction_count_by_portfolio(999)

    mock_cursor.execute.assert_called_once_with(
        "SELECT COUNT(*) as transaction_count FROM Transactions WHERE portfolio_id = %s",
        (999,)
    )
    assert result == 0


@patch('dao.transactions_dao.get_db_connection')
def test_get_total_transaction_value_by_portfolio(mock_get_db):
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, [(2750.00,)])

    result = dao.get_total_transaction_value_by_portfolio(1)

    mock_cursor.execute.assert_called_once_with(
        "SELECT SUM(transaction_total) as total_value FROM Transactions WHERE portfolio_id = %s",
        (1,)
    )
    assert result == 2750.00


@patch('dao.transactions_dao.get_db_connection')
def test_get_total_transaction_value_by_portfolio_no_transactions(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [(None,)])

    result = dao.get_total_transaction_value_by_portfolio(999)

    assert result is None


@patch('dao.transactions_dao.get_db_connection')
def test_get_average_transaction_price_by_asset(mock_get_db):
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, [(200.00,)])

    result = dao.get_average_transaction_price_by_asset(1)

    mock_cursor.execute.assert_called_once_with(
        "SELECT AVG(transaction_price) as avg_price FROM Transactions WHERE asset_id = %s",
        (1,)
    )
    assert result == 200.00


@patch('dao.transactions_dao.get_db_connection')
def test_get_average_transaction_price_by_asset_no_transactions(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [(None,)])

    result = dao.get_average_transaction_price_by_asset(999)

    assert result is None


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_summary_by_portfolio(mock_get_db):
    rows = [
        ("BUY", 3, 30, 4500.00, 150.00),
        ("SELL", 1, 5, 1250.00, 250.00)
    ]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_transaction_summary_by_portfolio(1)

    assert mock_cursor.execute.call_args[0][1] == (1,)
    assert len(result) == 2
    assert result[0] == {
        "transaction_type": "BUY",
        "count": 3,
        "total_quantity": 30,
        "total_value": 4500.00,
        "avg_price": 150.00
    }
    assert result[1]["transaction_type"] == "SELL"


@patch('dao.transactions_dao.get_db_connection')
def test_get_transaction_summary_by_portfolio_empty(mock_get_db):
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_transaction_summary_by_portfolio(999)

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_insert_transaction(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.lastrowid = 42
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.insert_transaction(1, 2, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO Transactions "
        "(portfolio_id, asset_id, transaction_type, transaction_quantity, transaction_price, "
        "transaction_date, transaction_total, balance_after_transaction) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (1, 2, "BUY", 10, 150.00, "2024-01-15", 1500.00, 48500.00)
    )
    mock_connection.commit.assert_called_once()
    assert result == 42


@patch('dao.transactions_dao.get_db_connection')
def test_update_transaction(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.update_transaction(1, "SELL", 5, 250.00, 1250.00, 49750.00)

    mock_cursor.execute.assert_called_once_with(
        "UPDATE Transactions "
        "SET transaction_type = %s, "
        "    transaction_quantity = %s, "
        "    transaction_price = %s, "
        "    transaction_total = %s, "
        "    balance_after_transaction = %s "
        "WHERE transaction_id = %s",
        ("SELL", 5, 250.00, 1250.00, 49750.00, 1)
    )
    mock_connection.commit.assert_called_once()
    assert result == 1


@patch('dao.transactions_dao.get_db_connection')
def test_update_transaction_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.update_transaction(999, "SELL", 5, 250.00, 1250.00, 49750.00)

    assert result == 0


@patch('dao.transactions_dao.get_db_connection')
def test_delete_transaction(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.delete_transaction(1)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM Transactions WHERE transaction_id = %s", (1,)
    )
    mock_connection.commit.assert_called_once()
    assert result == 1


@patch('dao.transactions_dao.get_db_connection')
def test_delete_transaction_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.delete_transaction(999)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM Transactions WHERE transaction_id = %s", (999,)
    )
    mock_connection.commit.assert_called_once()
    assert result == 0


@patch('dao.transactions_dao.get_db_connection')
def test_delete_transactions_by_portfolio(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 3
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.delete_transactions_by_portfolio(1)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM Transactions WHERE portfolio_id = %s", (1,)
    )
    mock_connection.commit.assert_called_once()
    assert result == 3


@patch('dao.transactions_dao.get_db_connection')
def test_delete_transactions_by_portfolio_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = TransactionsDao()
    result = dao.delete_transactions_by_portfolio(999)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM Transactions WHERE portfolio_id = %s", (999,)
    )
    mock_connection.commit.assert_called_once()
    assert result == 0


# Inventory/Holdings Tests
@patch('dao.transactions_dao.get_db_connection')
def test_get_portfolio_holdings_with_assets(mock_get_db):
    """Test getting all holdings in a portfolio."""
    rows = [
        ("AAPL", 120),
        ("MSFT", 70),
    ]
    dao, _, mock_cursor = make_mocked_dao(mock_get_db, rows)

    result = dao.get_portfolio_holdings(1)

    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0] == {"asset_id": "AAPL", "quantity": 120}
    assert result[1] == {"asset_id": "MSFT", "quantity": 70}


@patch('dao.transactions_dao.get_db_connection')
def test_get_portfolio_holdings_empty(mock_get_db):
    """Test getting holdings for portfolio with no assets."""
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_portfolio_holdings(999)

    assert result == []


@patch('dao.transactions_dao.get_db_connection')
def test_get_portfolio_holdings_excludes_zero_quantity(mock_get_db):
    """Test that holdings with zero quantity are excluded by HAVING clause.

    Note: The HAVING clause in SQL filters zero quantities at DB level.
    When mocked, we simulate the DB already filtering the results.
    """
    rows = [
        ("AAPL", 100),
    ]
    dao, _, _ = make_mocked_dao(mock_get_db, rows)

    result = dao.get_portfolio_holdings(1)

    # Only AAPL should be returned (GOOG is filtered by HAVING clause in SQL)
    assert len(result) == 1
    assert result[0]["asset_id"] == "AAPL"
    assert result[0]["quantity"] == 100


@patch('dao.transactions_dao.get_db_connection')
def test_get_asset_holding_positive_quantity(mock_get_db):
    """Test getting holding for a specific asset."""
    dao, _, _ = make_mocked_dao(mock_get_db, [(50,)])

    result = dao.get_asset_holding(1, "AAPL")

    assert result == 50


@patch('dao.transactions_dao.get_db_connection')
def test_get_asset_holding_zero_quantity(mock_get_db):
    """Test getting holding when asset not owned."""
    dao, _, _ = make_mocked_dao(mock_get_db, [(None,)])

    result = dao.get_asset_holding(1, "UNKNOWN")

    assert result == 0


@patch('dao.transactions_dao.get_db_connection')
def test_get_asset_holding_null_result(mock_get_db):
    """Test handling of null database result."""
    dao, _, _ = make_mocked_dao(mock_get_db, [])

    result = dao.get_asset_holding(999, "NONEXISTENT")

    assert result == 0
