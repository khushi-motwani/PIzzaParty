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

@transactions_bp.route('/create', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()

        # Validate required fields
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
