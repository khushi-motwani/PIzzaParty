import logging
from service.transactions_service import TransactionsService
from exception.validation_exceptions import (
    ValidationException,
    PortfolioNotFoundException,
    AssetNotFoundException,
    InsufficientAssetQuantityException,
    InsufficientFundsException
)
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

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
    transaction = transactions_service.get_transaction_by_id(transaction_id)
    return jsonify(transaction.to_dict())

@transactions_bp.route('/portfolio/<int:portfolio_id>/all', methods=['GET'])
def get_transactions_by_portfolio(portfolio_id):
    transactions = transactions_service.get_transactions_by_portfolio(portfolio_id)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/portfolio/<int:portfolio_id>/count', methods=['GET'])
def get_portfolio_transaction_count(portfolio_id):
    count = transactions_service.get_transaction_count_by_portfolio(portfolio_id)
    return jsonify({"count": count})

@transactions_bp.route('/portfolio/<int:portfolio_id>/value', methods=['GET'])
def get_portfolio_transaction_value(portfolio_id):
    total_value = transactions_service.get_total_transaction_value_by_portfolio(portfolio_id)
    return jsonify({"total_value": total_value})

@transactions_bp.route('/portfolio/<int:portfolio_id>/asset/<asset_id>/all', methods=['GET'])
def get_transactions_by_asset(portfolio_id, asset_id):
    transactions = transactions_service.get_transactions_by_asset(portfolio_id, asset_id)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/type/<transaction_type>/all', methods=['GET'])
def get_transactions_by_type(transaction_type):
    transactions = transactions_service.get_transactions_by_type(transaction_type)
    return jsonify([transaction.to_dict() for transaction in transactions])

@transactions_bp.route('/portfolio/<int:portfolio_id>/summary', methods=['GET'])
def get_transaction_summary(portfolio_id):
    summary = transactions_service.get_transaction_summary_by_portfolio(portfolio_id)
    return jsonify(summary)

@transactions_bp.route('/portfolio/<int:portfolio_id>/holdings', methods=['GET'])
def get_portfolio_holdings(portfolio_id):
    try:
        holdings = transactions_service.get_portfolio_holdings(portfolio_id)
        return jsonify(holdings), 200
    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.critical(f"Error retrieving holdings: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/portfolio/<int:portfolio_id>/holdings/<asset_id>', methods=['GET'])
def get_asset_holding(portfolio_id, asset_id):
    try:
        holding = transactions_service.get_asset_holding(portfolio_id, asset_id)
        return jsonify(holding), 200
    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except AssetNotFoundException as e:
        logger.critical(f"Asset not found: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.critical(f"Error retrieving asset holding: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

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

    except InsufficientAssetQuantityException as e:
        logger.warning(f"Insufficient asset quantity error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except ValidationException as e:
        logger.critical(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.critical(f"Internal server error during transaction creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/create_buy', methods=['POST'])
@cross_origin()
def create_buy_transaction():
    try:
        data = request.get_json()

        required_fields = ['portfolio_id', 'asset_id', 'quantity', 'price']
        if not all(field in data for field in required_fields):
            logger.warning(f"Create BUY transaction request missing required fields: {required_fields}")
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400

        portfolio_id = data['portfolio_id']
        asset_id = data['asset_id']
        quantity = data['quantity']
        price = data['price']

        transaction_id = transactions_service.create(
            portfolio_id, asset_id, 'BUY', quantity, price, None, None, None
        )

        return jsonify({
            "message": "BUY transaction created successfully",
            "transaction_id": transaction_id
        }), 201

    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found error: {str(e)}")
        return jsonify({"error": "Portfolio not found"}), 404

    except AssetNotFoundException as e:
        logger.critical(f"Asset not found error: {str(e)}")
        return jsonify({"error": "Asset not found"}), 404


    except ValidationException as e:
        logger.critical(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.critical(f"Internal server error during BUY transaction creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/create_sell', methods=['POST'])
@cross_origin()
def create_sell_transaction():
    try:
        data = request.get_json()

        required_fields = ['portfolio_id', 'asset_id', 'quantity', 'price']
        if not all(field in data for field in required_fields):
            logger.warning(f"Create SELL transaction request missing required fields: {required_fields}")
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400

        portfolio_id = data['portfolio_id']
        asset_id = data['asset_id']
        quantity = data['quantity']
        price = data['price']

        transaction_id = transactions_service.create(
            portfolio_id, asset_id, 'SELL', quantity, price, None, None, None
        )

        return jsonify({
            "message": "SELL transaction created successfully",
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
        logger.critical(f"Internal server error during SELL transaction creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/create_deposit', methods=['POST'])
@cross_origin()
def create_deposit_transaction():
    try:
        data = request.get_json()

        required_fields = ['portfolio_id', 'amount']
        if not all(field in data for field in required_fields):
            logger.warning(f"Create DEPOSIT transaction request missing required fields: {required_fields}")
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400

        portfolio_id = int(data['portfolio_id'])
        amount = float(data['amount'])

        transaction_id = transactions_service.create(
            portfolio_id, None, 'DEPOSIT', None, None, None, amount, None
        )

        return jsonify({
            "message": "DEPOSIT transaction created successfully",
            "transaction_id": transaction_id
        }), 201

    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found error: {str(e)}")
        return jsonify({"error": str(e)}), 404

    except ValidationException as e:
        logger.critical(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.critical(f"Internal server error during DEPOSIT transaction creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@transactions_bp.route('/create_withdrawal', methods=['POST'])
@cross_origin()
def create_withdrawal_transaction():
    try:
        data = request.get_json()

        required_fields = ['portfolio_id', 'amount']
        if not all(field in data for field in required_fields):
            logger.warning(f"Create WITHDRAWAL transaction request missing required fields: {required_fields}")
            return jsonify({
                "error": "Missing required fields",
                "required": required_fields
            }), 400

        portfolio_id = int(data['portfolio_id'])
        amount = float(data['amount'])

        transaction_id = transactions_service.create(
            portfolio_id, None, 'WITHDRAW', None, None, None, amount, None
        )

        return jsonify({
            "message": "WITHDRAWAL transaction created successfully",
            "transaction_id": transaction_id
        }), 201

    except PortfolioNotFoundException as e:
        logger.critical(f"Portfolio not found error: {str(e)}")
        return jsonify({"error": str(e)}), 404

    except InsufficientFundsException as e:
        logger.warning(f"Insufficient funds error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except ValidationException as e:
        logger.critical(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.critical(f"Internal server error during WITHDRAWAL transaction creation: {str(e)}", exc_info=True)
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

        transactions_service.update_transaction(
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
        transactions_service.delete_transaction(transaction_id)
        logger.info(f"Transaction deleted successfully: ID={transaction_id}")
        return jsonify({
            "message": "Transaction deleted successfully",
            "transaction_id": transaction_id
        }), 200

    except Exception as e:
        logger.critical(f"Error deleting transaction: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
