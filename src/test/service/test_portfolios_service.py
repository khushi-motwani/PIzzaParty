import pytest
from unittest.mock import MagicMock, patch
from service.portfolios_service import PortfoliosService
from dto.portfolios_dto import PortfoliosDTO
from exception.validation_exceptions import (
    PortfolioNotFoundException,
    InvalidPortfolioNameException,
    InvalidAmountException,
    InsufficientFundsException
)


class TestPortfoliosService:
    """Test PortfoliosService methods."""

    @pytest.fixture
    def service(self):
        """Create service with mocked DAO."""
        with patch('service.portfolios_service.PortfoliosDao'):
            return PortfoliosService()

    @pytest.fixture
    def mock_portfolio(self):
        """Create a mock portfolio."""
        return PortfoliosDTO(
            portfolio_name="Test Portfolio",
            portfolio_id=1,
            portfolio_balance=50000.00
        )

    def test_get_all(self, service):
        """Test get_all returns list of portfolios."""
        portfolios = [
            PortfoliosDTO("Portfolio 1", 1, 50000.00),
            PortfoliosDTO("Portfolio 2", 2, 100000.00)
        ]
        service.portfolios_dao.get_all = MagicMock(return_value=portfolios)

        result = service.get_all()

        assert len(result) == 2
        assert result[0].portfolio_name == "Portfolio 1"
        assert result[1].portfolio_name == "Portfolio 2"
        service.portfolios_dao.get_all.assert_called_once()

    def test_get_all_empty(self, service):
        """Test get_all returns empty list when no portfolios."""
        service.portfolios_dao.get_all = MagicMock(return_value=[])

        result = service.get_all()

        assert result == []
        service.portfolios_dao.get_all.assert_called_once()

    def test_get_by_id_success(self, service, mock_portfolio):
        """Test get_by_id returns portfolio."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=mock_portfolio)

        result = service.get_by_id(1)

        assert result.portfolio_id == 1
        assert result.portfolio_name == "Test Portfolio"
        assert result.portfolio_balance == 50000.00
        service.portfolios_dao.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self, service):
        """Test get_by_id raises exception when not found."""
        service.portfolios_dao.get_by_id = MagicMock(
            side_effect=PortfolioNotFoundException(999)
        )

        with pytest.raises(PortfolioNotFoundException):
            service.get_by_id(999)

        service.portfolios_dao.get_by_id.assert_called_once_with(999)

    def test_get_portfolio_balance(self, service, mock_portfolio):
        """Test get_portfolio_balance returns portfolio."""
        service.portfolios_dao.get_portfolio_balance = MagicMock(return_value=mock_portfolio)

        result = service.get_portfolio_balance(1)

        assert result.portfolio_id == 1
        assert result.portfolio_balance == 50000.00
        service.portfolios_dao.get_portfolio_balance.assert_called_once_with(1)

    def test_get_portfolio_balance_not_found(self, service):
        """Test get_portfolio_balance raises exception when not found."""
        service.portfolios_dao.get_portfolio_balance = MagicMock(
            side_effect=PortfolioNotFoundException(999)
        )

        with pytest.raises(PortfolioNotFoundException):
            service.get_portfolio_balance(999)

    def test_get_total_balance(self, service):
        """Test get_total_balance returns total."""
        service.portfolios_dao.get_total_balance = MagicMock(return_value=150000.00)

        result = service.get_total_balance()

        assert result == 150000.00
        service.portfolios_dao.get_total_balance.assert_called_once()

    def test_get_total_balance_empty(self, service):
        """Test get_total_balance returns 0 when no portfolios."""
        service.portfolios_dao.get_total_balance = MagicMock(return_value=0)

        result = service.get_total_balance()

        assert result == 0

    def test_get_count(self, service):
        """Test get_count returns portfolio count."""
        service.portfolios_dao.get_count = MagicMock(return_value=5)

        result = service.get_count()

        assert result == 5
        service.portfolios_dao.get_count.assert_called_once()

    def test_count(self, service):
        """Test count returns portfolio count."""
        service.portfolios_dao.count = MagicMock(return_value=3)

        result = service.count()

        assert result == 3
        service.portfolios_dao.count.assert_called_once()

    def test_get_sorted_by_balance_desc(self, service):
        """Test get_sorted_by_balance_desc returns sorted portfolios."""
        portfolios = [
            PortfoliosDTO("High Balance", 2, 100000.00),
            PortfoliosDTO("Low Balance", 1, 50000.00)
        ]
        service.portfolios_dao.get_sorted_by_balance_desc = MagicMock(return_value=portfolios)

        result = service.get_sorted_by_balance_desc()

        assert len(result) == 2
        assert result[0].portfolio_balance == 100000.00
        assert result[1].portfolio_balance == 50000.00
        service.portfolios_dao.get_sorted_by_balance_desc.assert_called_once()

    def test_get_sorted_by_balance_asc(self, service):
        """Test get_sorted_by_balance_asc returns sorted portfolios."""
        portfolios = [
            PortfoliosDTO("Low Balance", 1, 50000.00),
            PortfoliosDTO("High Balance", 2, 100000.00)
        ]
        service.portfolios_dao.get_sorted_by_balance_asc = MagicMock(return_value=portfolios)

        result = service.get_sorted_by_balance_asc()

        assert len(result) == 2
        assert result[0].portfolio_balance == 50000.00
        assert result[1].portfolio_balance == 100000.00
        service.portfolios_dao.get_sorted_by_balance_asc.assert_called_once()

    def test_create_with_balance(self, service):
        """Test create returns new portfolio ID."""
        service.portfolios_dao.create = MagicMock(return_value=1)

        result = service.create("New Portfolio", 50000.00)

        assert result == 1
        service.portfolios_dao.create.assert_called_once_with("New Portfolio", 50000.00)

    def test_create_with_default_balance(self, service):
        """Test create with default balance."""
        service.portfolios_dao.create = MagicMock(return_value=2)

        result = service.create("New Portfolio")

        assert result == 2
        service.portfolios_dao.create.assert_called_once_with("New Portfolio", 0)

    def test_create_multiple_portfolios(self, service):
        """Test creating multiple portfolios returns different IDs."""
        service.portfolios_dao.create = MagicMock(side_effect=[1, 2, 3])

        result1 = service.create("Portfolio 1", 1000.00)
        result2 = service.create("Portfolio 2", 2000.00)
        result3 = service.create("Portfolio 3", 3000.00)

        assert result1 == 1
        assert result2 == 2
        assert result3 == 3
        assert service.portfolios_dao.create.call_count == 3

    def test_update_name_success(self, service):
        """Test update_name returns True on success."""
        service.portfolios_dao.update_name = MagicMock(return_value=True)

        result = service.update_name(1, "Updated Name")

        assert result is True
        service.portfolios_dao.update_name.assert_called_once_with(1, "Updated Name")

    def test_update_name_not_found(self, service):
        """Test update_name returns False when portfolio not found."""
        service.portfolios_dao.update_name = MagicMock(return_value=False)

        result = service.update_name(999, "Updated Name")

        assert result is False

    def test_update_balance_success(self, service):
        """Test update_balance returns True on success."""
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        result = service.update_balance(1, 75000.00)

        assert result is True
        service.portfolios_dao.update_balance.assert_called_once_with(1, 75000.00)

    def test_update_balance_not_found(self, service):
        """Test update_balance returns False when portfolio not found."""
        service.portfolios_dao.update_balance = MagicMock(return_value=False)

        result = service.update_balance(999, 75000.00)

        assert result is False

    def test_update_balance_to_zero(self, service):
        """Test update_balance can set balance to zero."""
        service.portfolios_dao.update_balance = MagicMock(return_value=True)

        result = service.update_balance(1, 0)

        assert result is True
        service.portfolios_dao.update_balance.assert_called_once_with(1, 0)

    def test_update_balance_to_negative(self, service):
        """Test update_balance raises exception when setting balance to negative."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=MagicMock())

        with pytest.raises(ValueError, match="Balance cannot be negative"):
            service.update_balance(1, -1000.00)

    def test_increment_balance_success(self, service):
        """Test increment_balance returns True on success."""
        service.portfolios_dao.increment_balance = MagicMock(return_value=True)

        result = service.increment_balance(1, 10000.00)

        assert result is True
        service.portfolios_dao.increment_balance.assert_called_once_with(1, 10000.00)

    def test_increment_balance_not_found(self, service):
        """Test increment_balance returns False when portfolio not found."""
        service.portfolios_dao.increment_balance = MagicMock(return_value=False)

        result = service.increment_balance(999, 10000.00)

        assert result is False

    def test_increment_balance_large_amount(self, service):
        """Test increment_balance with large amount."""
        service.portfolios_dao.increment_balance = MagicMock(return_value=True)

        result = service.increment_balance(1, 1000000.00)

        assert result is True
        service.portfolios_dao.increment_balance.assert_called_once_with(1, 1000000.00)

    def test_decrement_balance_success(self, service, mock_portfolio):
        """Test decrement_balance returns True on success."""
        service.portfolios_dao.get_portfolio_balance = MagicMock(return_value=mock_portfolio)
        service.portfolios_dao.decrement_balance = MagicMock(return_value=True)

        result = service.decrement_balance(1, 5000.00)

        assert result is True
        service.portfolios_dao.get_portfolio_balance.assert_called_once_with(1)
        service.portfolios_dao.decrement_balance.assert_called_once_with(1, 5000.00)

    def test_decrement_balance_not_found(self, service):
        """Test decrement_balance raises exception when portfolio not found."""
        service.portfolios_dao.get_by_id = MagicMock(
            side_effect=PortfolioNotFoundException(999)
        )

        with pytest.raises(PortfolioNotFoundException):
            service.decrement_balance(999, 5000.00)

    def test_decrement_balance_large_amount(self, service):
        """Test decrement_balance with large amount."""
        large_balance_portfolio = PortfoliosDTO("Rich Portfolio", 1, 1000000.00)
        service.portfolios_dao.get_portfolio_balance = MagicMock(return_value=large_balance_portfolio)
        service.portfolios_dao.decrement_balance = MagicMock(return_value=True)

        result = service.decrement_balance(1, 500000.00)

        assert result is True
        service.portfolios_dao.get_portfolio_balance.assert_called_once_with(1)
        service.portfolios_dao.decrement_balance.assert_called_once_with(1, 500000.00)

    def test_delete_success(self, service):
        """Test delete returns True on success."""
        service.portfolios_dao.delete = MagicMock(return_value=True)

        result = service.delete(1)

        assert result is True
        service.portfolios_dao.delete.assert_called_once_with(1)

    def test_delete_not_found(self, service):
        """Test delete returns False when portfolio not found."""
        service.portfolios_dao.delete = MagicMock(return_value=False)

        result = service.delete(999)

        assert result is False

    def test_multiple_operations_in_sequence(self, service):
        """Test multiple service operations in sequence."""
        portfolio = PortfoliosDTO("Test Portfolio", 1, 50000.00)

        service.portfolios_dao.create = MagicMock(return_value=1)
        service.portfolios_dao.get_by_id = MagicMock(return_value=portfolio)
        service.portfolios_dao.update_balance = MagicMock(return_value=True)
        service.portfolios_dao.increment_balance = MagicMock(return_value=True)
        service.portfolios_dao.get_total_balance = MagicMock(return_value=60000.00)

        # Create portfolio
        new_id = service.create("Test Portfolio", 50000.00)
        assert new_id == 1

        # Get portfolio
        portfolio = service.get_by_id(1)
        assert portfolio.portfolio_id == 1

        # Update balance
        updated = service.update_balance(1, 60000.00)
        assert updated is True

        # Increment balance
        incremented = service.increment_balance(1, 5000.00)
        assert incremented is True

        # Get total
        total = service.get_total_balance()
        assert total == 60000.00

    def test_get_all_and_sorted_operations(self, service):
        """Test getting all and sorted portfolios."""
        portfolios_asc = [
            PortfoliosDTO("Low", 1, 10000.00),
            PortfoliosDTO("High", 2, 100000.00)
        ]
        portfolios_desc = [
            PortfoliosDTO("High", 2, 100000.00),
            PortfoliosDTO("Low", 1, 10000.00)
        ]

        service.portfolios_dao.get_all = MagicMock(return_value=portfolios_asc)
        service.portfolios_dao.get_sorted_by_balance_asc = MagicMock(return_value=portfolios_asc)
        service.portfolios_dao.get_sorted_by_balance_desc = MagicMock(return_value=portfolios_desc)

        all_portfolios = service.get_all()
        assert len(all_portfolios) == 2

        asc_portfolios = service.get_sorted_by_balance_asc()
        assert asc_portfolios[0].portfolio_balance == 10000.00

        desc_portfolios = service.get_sorted_by_balance_desc()
        assert desc_portfolios[0].portfolio_balance == 100000.00

    def test_decrement_balance_insufficient_funds(self, service):
        """Test decrement_balance raises InsufficientFundsException when not enough balance."""
        low_balance_portfolio = PortfoliosDTO("Poor Portfolio", 1, 1000.00)
        service.portfolios_dao.get_by_id = MagicMock(return_value=MagicMock())
        service.portfolios_dao.get_portfolio_balance = MagicMock(return_value=low_balance_portfolio)

        with pytest.raises(InsufficientFundsException):
            service.decrement_balance(1, 5000.00)

    def test_create_with_empty_name(self, service):
        """Test create raises InvalidPortfolioNameException with empty name."""
        with pytest.raises(InvalidPortfolioNameException):
            service.create("", 50000.00)

    def test_create_with_none_name(self, service):
        """Test create raises InvalidPortfolioNameException with None name."""
        with pytest.raises(InvalidPortfolioNameException):
            service.create(None, 50000.00)

    def test_create_with_negative_balance(self, service):
        """Test create raises ValueError with negative balance."""
        with pytest.raises(ValueError, match="Balance cannot be negative"):
            service.create("Portfolio", -1000.00)

    def test_increment_balance_with_zero_amount(self, service):
        """Test increment_balance raises InvalidAmountException with zero amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=MagicMock())

        with pytest.raises(InvalidAmountException):
            service.increment_balance(1, 0)

    def test_increment_balance_with_negative_amount(self, service):
        """Test increment_balance raises InvalidAmountException with negative amount."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=MagicMock())

        with pytest.raises(InvalidAmountException):
            service.increment_balance(1, -5000.00)

    def test_update_name_with_empty_name(self, service):
        """Test update_name raises InvalidPortfolioNameException with empty name."""
        service.portfolios_dao.get_by_id = MagicMock(return_value=MagicMock())

        with pytest.raises(InvalidPortfolioNameException):
            service.update_name(1, "")
