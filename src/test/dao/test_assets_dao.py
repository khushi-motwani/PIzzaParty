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
       ('AAPL', 'Apple', 'STOCK', 'Technology', 'Hardware', True),
        ('TSLA', 'Tesla', 'STOCK', 'Technology', 'Auto Manufacturers', False)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_all()
    print(result)
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


@patch('dao.assets_dao.get_db_connection')
def test_get_by_id(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = ('AAPL', 'Apple', 'STOCK', 'Technology', 'Hardware', True)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_by_id(1)

    assert result.asset_id == "AAPL"
    assert result.asset_name == "Apple"
    assert result.asset_type == "STOCK"
    assert result.is_favourite is True


@patch('dao.assets_dao.get_db_connection')
def test_get_by_id_not_found(mock_get_db):
    from exception.validation_exceptions import AssetNotFoundException
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = None
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    try:
        dao.get_by_id(999)
        assert False, "Should have raised AssetNotFoundException"
    except AssetNotFoundException:
        assert True


@patch('dao.assets_dao.get_db_connection')
def test_get_all_favourite_assets(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        ('AAPL', 'Apple', 'STOCK', 'Technology', 'Hardware', True),
        ('MSFT', "Microsoft", "STOCK", "Technology", "Software", True)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_all_favourite_assets()

    assert len(result) == 2
    assert result[0].asset_name == "Apple"
    assert result[1].asset_name == "Microsoft"
    assert all(asset.is_favourite is True for asset in result)


@patch('dao.assets_dao.get_db_connection')
def test_get_all_favourite_assets_empty(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_all_favourite_assets()

    assert result == []


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_type(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
       ('AAPL', 'Apple', 'STOCK', 'Technology', 'Hardware', True),
       ('TSLA', 'Tesla', 'STOCK', 'Technology', 'Auto Manufacturers', False)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_type("STOCK")

    assert len(result) == 2
    assert all(asset.asset_type == "STOCK" for asset in result)


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_type_empty(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_type("CRYPTO")

    assert result == []


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_sector(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        ('AAPL', 'Apple', 'STOCK', 'Technology', 'Hardware', True),
        ('MSFT', "Microsoft", "STOCK", "Technology", "Software", True)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_sector("Technology")

    assert len(result) == 2
    assert all(asset.asset_sector == "Technology" for asset in result)


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_sector_empty(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_sector("UnknownSector")

    assert result == []


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_industry(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = [
        ("AAPL", "Apple", "STOCK", "Technology", "Hardware", True)
    ]
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_industry("Hardware")

    assert len(result) == 1
    assert result[0].asset_industry == "Hardware"


@patch('dao.assets_dao.get_db_connection')
def test_get_assets_by_industry_empty(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_assets_by_industry("UnknownIndustry")

    assert result == []


@patch('dao.assets_dao.get_db_connection')
def test_get_favourite_asset_count(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (3,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_favourite_asset_count()

    assert result == 3


@patch('dao.assets_dao.get_db_connection')
def test_get_favourite_asset_count_zero(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_cursor.fetchone.return_value = (0,)
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    result = dao.get_favourite_asset_count()

    assert result == 0


@patch('dao.assets_dao.get_db_connection')
def test_insert_asset(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    dao.insert_asset("GOOG", "Google", "STOCK", "Technology", "Software", True)

    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.assets_dao.get_db_connection')
def test_update_asset(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao() 
    dao.update_asset("AAPL", "Apple", "STOCK", "Technology", "Hardware")

    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.assets_dao.get_db_connection')
def test_update_asset_favourite_status(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    dao.update_asset_favourite_status(True, False)

    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()


@patch('dao.assets_dao.get_db_connection')
def test_delete_asset(mock_get_db):
    mock_cursor = Mock()
    mock_connection = Mock()
    mock_connection.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_connection

    dao = AssetsDao()
    dao.delete_asset(1)

    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()
