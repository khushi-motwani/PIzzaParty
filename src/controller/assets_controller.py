from service.assets_service import AssetsService
from flask import Blueprint, jsonify, request

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')

assets_service = AssetsService()

@assets_bp.route('/all', methods=['GET'])
def get_all_assets():
    assets = assets_service.get_all()
    return jsonify([asset.to_dict() for asset in assets])

@assets_bp.route('/count', methods=['GET'])
def get_assets_count():
    count = assets_service.count()
    return jsonify({"count": count})

@assets_bp.route('/favourite', methods=['PUT'])
def update_favourite_status():
    data = request.get_json()
    asset_id = data.get('asset_id')
    is_favourite = data.get('is_favourite')
    assets_service.update_favourite_status(asset_id, is_favourite)
    return jsonify({"message": "Favourite status updated successfully"})