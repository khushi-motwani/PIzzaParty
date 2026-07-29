import logging
from service.transactions_service import TransactionsService
from exception.validation_exceptions import ValidationException, PortfolioNotFoundException, AssetNotFoundException
from flask import Blueprint, jsonify, request

logger = logging.getLogger('pizzaparty')

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

transactions_service = TransactionsService()

@transactions_bp.route('/all', methods=['GET'])
def get_all_transactions():
    transactions = transactions_service.get_all()
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/count', methods=['GET'])
def get_transactions_count():
    count = transactions_service.count()
    return jsonify({"count": count})

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = transactions_service.transactions_dao.get_transaction_by_id(transaction_id)
    return jsonify(transaction.to_dict())

@transactions_bp.route('/portfolio/<int:portfolio_id>/all', methods=['GET'])
def get_transactions_by_portfolio(portfolio_id):
    transactions = transactions_service.transactions_dao.get_transactions_by_portfolio(portfolio_id)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/portfolio/<int:portfolio_id>/count', methods=['GET'])
def get_portfolio_transaction_count(portfolio_id):
    count = transactions_service.transactions_dao.get_transaction_count_by_portfolio(portfolio_id)
    return jsonify({"count": count})

@transactions_bp.route('/portfolio/<int:portfolio_id>/value', methods=['GET'])
def get_portfolio_transaction_value(portfolio_id):
    total_value = transactions_service.transactions_dao.get_total_transaction_value_by_portfolio(portfolio_id)
    return jsonify({"total_value": total_value})

@transactions_bp.route('/portfolio/<int:portfolio_id>/asset/<asset_id>/all', methods=['GET'])
def get_transactions_by_asset(portfolio_id, asset_id):
    transactions = transactions_service.transactions_dao.get_transactions_by_asset(portfolio_id, asset_id)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/type/<transaction_type>/all', methods=['GET'])
def get_transactions_by_type(transaction_type):
    transactions = transactions_service.transactions_dao.get_transactions_by_type(transaction_type)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/portfolio/<int:portfolio_id>/summary', methods=['GET'])
def get_transaction_summary(portfolio_id):
    summary = transactions_service.transactions_dao.get_transaction_summary_by_portfolio(portfolio_id)
    return jsonify(summary)

@transactions_bp.route('/create', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()

        required_fields = ['portfolio_id', 'asset_id', 'transaction_type', 'quantity', 'price']
        if not all(field in data for field in required_fields):
            logger.warning(f"Create transaction request missing required fields: {required_fields}")
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400

        portfolio_id = data['portfolio_id']
        asset_id = data['asset_id']
        transaction_type = data['transaction_type']
        quantity = data['quantity']
        price = data['price']

        transaction_id = transactions_service.create_transaction(
            portfolio_id, asset_id, transaction_type, quantity, price
        )

        return jsonify({
            "message": "Transaction created successfully",
            "transaction_id": transaction_id
        }), 201

    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found error: {str(e)}")
        return jsonify({"error": str(e)}), 404

    except AssetNotFoundException as e:
        logger.critical(f"Asset not found error: {str(e)}")
        return jsonify({"error": str(e)}), 404

    except ValidationException as e:
        logger.critical(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.critical(f"Internal server error during transaction creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    try:
        data = request.get_json()

        transaction_type = data['transaction_type']
        transaction_quantity = data['transaction_quantity']
        transaction_price = data['transaction_price']
        transaction_total = data['transaction_total']
        balance_after_transaction = data['balance_after_transaction']

        transactions_service.transactions_dao.update_transaction(
            transaction_id, transaction_type, transaction_quantity,
            transaction_price, transaction_total, balance_after_transaction
        )

        logger.info(f"Transaction updated successfully: ID={transaction_id}, type={transaction_type}, quantity={transaction_quantity}")
        return jsonify({
            "message": "Transaction updated successfully",
            "transaction_id": transaction_id
        }), 200

    except ValidationException as e:
        logger.critical(f"Validation error updating transaction: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.critical(f"Error updating transaction: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        transactions_service.transactions_dao.delete_transaction(transaction_id)
        logger.info(f"Transaction deleted successfully: ID={transaction_id}")
        return jsonify({
            "message": "Transaction deleted successfully",
            "transaction_id": transaction_id
        }), 200

    except Exception as e:
        logger.critical(f"Error deleting transaction: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
