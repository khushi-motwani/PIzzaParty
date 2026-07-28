from unittest.mock import patch
from controller.finance_controller import get_quote
from dto.quote_dto import QuoteDTO
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError


@patch('controller.finance_controller.finance_service')
def test_get_quote_success(mock_service, app_context):
    quote = QuoteDTO(
        ticker="AAPL",
        price=150.5,
        currency="USD",
        previous_close=149.75,
        market_cap=2400000000000,
        day_high=151.2,
        day_low=148.9
    )
    mock_service.get_quote.return_value = quote

    result = get_quote("AAPL")

    data = result[0].json
    assert data["ticker"] == "AAPL"
    assert data["price"] == 150.5
    assert data["currency"] == "USD"
    assert result[1] == 200
    mock_service.get_quote.assert_called_once_with("AAPL")


@patch('controller.finance_controller.finance_service')
def test_get_quote_ticker_not_found(mock_service, app_context):
    mock_service.get_quote.side_effect = TickerNotFoundError("Ticker 'NOTREAL' not found or has no price data")

    result = get_quote("NOTREAL")

    data = result[0].json
    assert "error" in data
    assert result[1] == 404
    mock_service.get_quote.assert_called_once_with("NOTREAL")


@patch('controller.finance_controller.finance_service')
def test_get_quote_api_error(mock_service, app_context):
    mock_service.get_quote.side_effect = FinanceApiError("Failed to fetch quote for ticker 'AAPL': Network error")

    result = get_quote("AAPL")

    data = result[0].json
    assert "error" in data
    assert result[1] == 502
    mock_service.get_quote.assert_called_once_with("AAPL")
