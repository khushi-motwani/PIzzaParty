from flask import Flask, jsonify
import logging
import logging.config
from flask import Flask, jsonify, request
from flask_cors import CORS
from controller.assets_controller import assets_bp
from controller.portfolios_controller import portfolios_bp
from controller.transactions_controller import transactions_bp
from controller.finance_controller import finance_bp

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('pizzaparty')

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Flask API!"}), 200

app.register_blueprint(assets_bp)
app.register_blueprint(portfolios_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(finance_bp)

if __name__ == '__main__':
    logger.info("Starting Flask application on 127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000)
    
    
