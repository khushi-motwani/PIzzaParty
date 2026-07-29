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

@assets_bp.route('/<asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = assets_service.get_by_id(asset_id)
    return jsonify(asset.to_dict())

@assets_bp.route('/favourite/all', methods=['GET'])
def get_favourite_assets():
    assets = assets_service.get_all_favourite_assets()
    return jsonify([asset.to_dict() for asset in assets])

@assets_bp.route('/favourite/count', methods=['GET'])
def get_favourite_assets_count():
    count = assets_service.get_favourite_asset_count()
    return jsonify({"count": count})

@assets_bp.route('/favourite', methods=['PUT'])
def update_favourite_status():
    data = request.get_json()
    asset_id = data.get('asset_id')
    is_favourite = data.get('is_favourite')
    assets_service.update_favourite_status(asset_id, is_favourite)
    return jsonify({"message": "Favourite status updated successfully"})

@assets_bp.route('/type/<asset_type>', methods=['GET'])
def get_assets_by_type(asset_type):
    assets = assets_service.get_assets_by_type(asset_type)
    return jsonify([asset.to_dict() for asset in assets])

@assets_bp.route('/sector/<asset_sector>', methods=['GET'])
def get_assets_by_sector(asset_sector):
    assets = assets_service.get_assets_by_sector(asset_sector)
    return jsonify([asset.to_dict() for asset in assets])

@assets_bp.route('/industry/<asset_industry>', methods=['GET'])
def get_assets_by_industry(asset_industry):
    assets = assets_service.get_assets_by_industry(asset_industry)
    return jsonify([asset.to_dict() for asset in assets])