from flask import Flask, jsonify
from controller.assets_controller import assets_bp
from controller.portfolios_controller import portfolios_bp
from controller.transactions_controller import transactions_bp
from controller.finance_controller import finance_bp


app = Flask(__name__)

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
    app.run(host='127.0.0.1', port=5000)
    
    
