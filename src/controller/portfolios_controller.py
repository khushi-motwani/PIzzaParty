from service.portfolios_service import PortfoliosService
from flask import Blueprint, jsonify, request

portfolios_bp = Blueprint('portfolios', __name__, url_prefix='/portfolios')

portfolios_service = PortfoliosService()

@portfolios_bp.route('/all', methods=['GET'])
def get_all_portfolios():
    portfolios = portfolios_service.get_all()
    return jsonify([portfolio.to_dict() for portfolio in portfolios])

@portfolios_bp.route('/count', methods=['GET'])
def get_portfolios_count():
    count = portfolios_service.count()
    return jsonify({"count": count})

@portfolios_bp.route('/<int:portfolio_id>', methods=['GET'])
def get_portfolio(portfolio_id):
    portfolio = portfolios_service.get_by_id(portfolio_id)
    return jsonify(portfolio.to_dict())

@portfolios_bp.route('/<int:portfolio_id>/balance', methods=['GET'])
def get_portfolio_balance(portfolio_id):
    portfolio = portfolios_service.get_portfolio_balance(portfolio_id)
    return jsonify({
        "portfolio_id": portfolio.portfolio_id,
        "portfolio_balance": portfolio.portfolio_balance
    })

@portfolios_bp.route('/total-balance', methods=['GET'])
def get_total_balance():
    total = portfolios_service.get_total_balance()
    return jsonify({"total_balance": total})

@portfolios_bp.route('/sorted/desc', methods=['GET'])
def get_sorted_by_balance_desc():
    portfolios = portfolios_service.get_sorted_by_balance_desc()
    return jsonify([portfolio.to_dict() for portfolio in portfolios])

@portfolios_bp.route('/sorted/asc', methods=['GET'])
def get_sorted_by_balance_asc():
    portfolios = portfolios_service.get_sorted_by_balance_asc()
    return jsonify([portfolio.to_dict() for portfolio in portfolios])

@portfolios_bp.route('/create', methods=['POST'])
def create_portfolio():
    data = request.get_json()
    portfolio_name = data['portfolio_name']
    portfolio_balance = data.get('portfolio_balance', 0)
    portfolio_id = portfolios_service.create(portfolio_name, portfolio_balance)
    return jsonify({
        "message": "Portfolio created successfully",
        "portfolio_id": portfolio_id
    })

@portfolios_bp.route('/<int:portfolio_id>/name', methods=['PUT'])
def update_portfolio_name(portfolio_id):
    data = request.get_json()
    portfolio_name = data['portfolio_name']
    portfolios_service.update_name(portfolio_id, portfolio_name)
    return jsonify({
        "message": "Portfolio name updated successfully",
        "portfolio_id": portfolio_id,
        "portfolio_name": portfolio_name
    })

@portfolios_bp.route('/<int:portfolio_id>/balance', methods=['PUT'])
def update_balance(portfolio_id):
    data = request.get_json()
    new_balance = data['portfolio_balance']
    portfolios_service.update_balance(portfolio_id, new_balance)
    return jsonify({
        "message": "Portfolio balance updated successfully",
        "portfolio_id": portfolio_id,
        "portfolio_balance": new_balance
    })

@portfolios_bp.route('/<int:portfolio_id>/increment', methods=['PUT'])
def increment_balance(portfolio_id):
    data = request.get_json()
    amount = data['amount']
    portfolios_service.increment_balance(portfolio_id, amount)
    return jsonify({
        "message": "Portfolio balance incremented successfully",
        "portfolio_id": portfolio_id,
        "amount": amount
    })

@portfolios_bp.route('/<int:portfolio_id>/decrement', methods=['PUT'])
def decrement_balance(portfolio_id):
    data = request.get_json()
    amount = data['amount']
    portfolios_service.decrement_balance(portfolio_id, amount)
    return jsonify({
        "message": "Portfolio balance decremented successfully",
        "portfolio_id": portfolio_id,
        "amount": amount
    })

@portfolios_bp.route('/<int:portfolio_id>', methods=['DELETE'])
def delete_portfolio(portfolio_id):
    try:
        portfolios_service.delete(portfolio_id)

        return jsonify({
            "message": "Portfolio deleted successfully",
            "portfolio_id": portfolio_id
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
