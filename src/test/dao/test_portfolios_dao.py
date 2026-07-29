import pytest
from unittest.mock import Mock, patch
from dao.portfolios_dao import PortfoliosDao
from exception.validation_exceptions import PortfolioNotFoundException

@patch('dao.portfolios_dao.get_db_connection')
def test_count_portfolios(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (3,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.count()

    assert result == 3
    assert dao.total == 3


@patch('dao.portfolios_dao.get_db_connection')
def test_get_all_portfolios(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        (1, "My Portfolio", 50000.00),
        (2, "Growth Portfolio", 100000.00)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_all()

    assert len(result) == 2
    assert result[0].portfolio_id == 1
    assert result[0].portfolio_name == "My Portfolio"
    assert result[0].portfolio_balance == 50000.00
    assert result[1].portfolio_id == 2
    assert result[1].portfolio_name == "Growth Portfolio"
    assert result[1].portfolio_balance == 100000.00


@patch('dao.portfolios_dao.get_db_connection')
def test_get_all_empty_table(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_all()

    assert result == []


@patch('dao.portfolios_dao.get_db_connection')
def test_get_by_id_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (1, "My Portfolio", 50000.00)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_by_id(1)

    assert result.portfolio_id == 1
    assert result.portfolio_name == "My Portfolio"
    assert result.portfolio_balance == 50000.00
    mock_cursor.execute.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_get_by_id_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = None
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()

    with pytest.raises(PortfolioNotFoundException):
        dao.get_by_id(999)


@patch('dao.portfolios_dao.get_db_connection')
def test_get_portfolio_balance(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (1, "My Portfolio", 50000.00)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_portfolio_balance(1)

    assert result.portfolio_id == 1
    assert result.portfolio_name == "My Portfolio"
    assert result.portfolio_balance == 50000.00


@patch('dao.portfolios_dao.get_db_connection')
def test_get_portfolio_balance_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = None
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()

    with pytest.raises(PortfolioNotFoundException):
        dao.get_portfolio_balance(999)


@patch('dao.portfolios_dao.get_db_connection')
def test_get_total_balance(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (150000.00,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_total_balance()

    assert result == 150000.00


@patch('dao.portfolios_dao.get_db_connection')
def test_get_total_balance_empty(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (None,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_total_balance()

    assert result == 0


@patch('dao.portfolios_dao.get_db_connection')
def test_get_count(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (5,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_count()

    assert result == 5
    assert dao.total == 5


@patch('dao.portfolios_dao.get_db_connection')
def test_get_sorted_by_balance_desc(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        (2, "Growth Portfolio", 100000.00),
        (1, "My Portfolio", 50000.00)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_sorted_by_balance_desc()

    assert len(result) == 2
    assert result[0].portfolio_balance == 100000.00
    assert result[1].portfolio_balance == 50000.00


@patch('dao.portfolios_dao.get_db_connection')
def test_get_sorted_by_balance_asc(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        (1, "My Portfolio", 50000.00),
        (2, "Growth Portfolio", 100000.00)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.get_sorted_by_balance_asc()

    assert len(result) == 2
    assert result[0].portfolio_balance == 50000.00
    assert result[1].portfolio_balance == 100000.00

@patch('dao.portfolios_dao.get_db_connection')
def test_create_portfolio(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.lastrowid = 3
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.create("New Portfolio", 75000.00)

    assert result == 3
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_create_portfolio_default_balance(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.lastrowid = 4
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.create("Default Portfolio")

    assert result == 4
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_update_name_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.update_name(1, "Updated Name")

    assert result is True
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_update_name_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.update_name(999, "Updated Name")

    assert result is False


@patch('dao.portfolios_dao.get_db_connection')
def test_update_balance_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.update_balance(1, 75000.00)

    assert result is True
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_update_balance_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.update_balance(999, 75000.00)

    assert result is False


@patch('dao.portfolios_dao.get_db_connection')
def test_increment_balance_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.increment_balance(1, 10000.00)

    assert result is True
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_increment_balance_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.increment_balance(999, 10000.00)

    assert result is False


@patch('dao.portfolios_dao.get_db_connection')
def test_decrement_balance_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.decrement_balance(1, 5000.00)

    assert result is True
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_decrement_balance_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.decrement_balance(999, 5000.00)

    assert result is False


@patch('dao.portfolios_dao.get_db_connection')
def test_delete_success(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 1
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.delete(1)

    assert result is True
    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.portfolios_dao.get_db_connection')
def test_delete_not_found(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.rowcount = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = PortfoliosDao()
    result = dao.delete(999)

    assert result is False
