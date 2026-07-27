from unittest.mock import patch
from controller.portfolios_controller import get_all_portfolios, get_portfolios_count
from dto.portfolios_dto import PortfoliosDTO

@patch('controller.portfolios_controller.portfolios_service')
def test_get_all_portfolios(mock_service, app_context):
    portfolio1 = PortfoliosDTO("My Portfolio", 50000.00)
    portfolio2 = PortfoliosDTO("Growth Portfolio", 100000.00)

    mock_service.get_all.return_value = [portfolio1, portfolio2]

    result = get_all_portfolios()

    data = result.json
    assert len(data) == 2
    assert data[0]["portfolio_name"] == "My Portfolio"
    assert data[1]["portfolio_name"] == "Growth Portfolio"
    mock_service.get_all.assert_called_once()
    
@patch('controller.portfolios_controller.portfolios_service')
def test_get_all_portfolios_empty(mock_service, app_context):
    mock_service.get_all.return_value = []

    result = get_all_portfolios()

    data = result.json
    assert len(data) == 0
    mock_service.get_all.assert_called_once()


@patch('controller.portfolios_controller.portfolios_service')
def test_get_portfolios_count(mock_service, app_context):
    mock_service.count.return_value = 3

    result = get_portfolios_count()

    data = result.json
    assert data["count"] == 3
    mock_service.count.assert_called_once()
