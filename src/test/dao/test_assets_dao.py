from unittest.mock import Mock, patch
from dao.assets_dao import AssetsDao


@patch('dao.assets_dao.get_db_connection')
def test_count_assets(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [(5,)]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.count()

    assert result == 5
    assert dao.total == 5


@patch('dao.assets_dao.get_db_connection')
def test_get_all_assets(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        (1, "Apple", "STOCK", "Technology", "Hardware", 1),
        (2, "Tesla", "STOCK", "Consumer", "Auto", 0)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_all()

    assert len(result) == 2
    assert result[0].asset_name == "Apple"
    assert result[1].asset_name == "Tesla"


@patch('dao.assets_dao.get_db_connection')
def test_get_all_empty_table(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_all()

    assert result == []
    assert len(result) == 0
