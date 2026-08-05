from service.finance_service import FinanceService
from flask import Blueprint, jsonify, request
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


@finance_bp.route('/history/<ticker>', methods=['GET'])
def get_history(ticker):
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        history = finance_service.get_history(ticker, start, end)
        return jsonify(history), 200
    except TickerNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except FinanceApiError as e:
        return jsonify({"error": str(e)}), 502
