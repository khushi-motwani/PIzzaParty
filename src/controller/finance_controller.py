from service.finance_service import FinanceService
from flask import Blueprint, jsonify
from exception.finance_exceptions import TickerNotFoundError, FinanceApiError

finance_bp = Blueprint('finance', __name__, url_prefix='/finance')

finance_service = FinanceService()


@finance_bp.route('/quote/<ticker>', methods=['GET'])
def get_quote(ticker):
    try:
        quote = finance_service.get_quote(ticker)
        return jsonify(quote.to_dict()), 200
    except TickerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except FinanceApiError as e:
        return jsonify({"error": str(e)}), 502
