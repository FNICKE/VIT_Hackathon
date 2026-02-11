from flask import Flask, request, jsonify
from datetime import datetime
from typing import Dict, List, Tuple
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# In-memory storage (replace with database)
users_db = {}
groups_db = {}
expenses_db = {}
settlements_db = {}
risk_scores_db = {}

# ==================== AUTHENTICATION & WALLET ====================

@app.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        if email in users_db:
            return jsonify({'message': 'Login successful', 'user_id': users_db[email]['id']}), 200
        
        # Create new user
        user_id = str(uuid.uuid4())
        users_db[email] = {
            'id': user_id,
            'email': email,
            'password': password,
            'wallet': None,
            'created_at': datetime.now().isoformat()
        }
        
        return jsonify({'message': 'User created and logged in', 'user_id': user_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/connect-wallet', methods=['POST'])
def connect_wallet():
    """Connect user's digital wallet"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        wallet_address = data.get('wallet_address')
        
        if not user_id or not wallet_address:
            return jsonify({'error': 'User ID and wallet address required'}), 400
        
        # Find user by ID and update wallet
        for email, user in users_db.items():
            if user['id'] == user_id:
                user['wallet'] = wallet_address
                user['wallet_verified'] = True
                return jsonify({'message': 'Wallet connected successfully', 'wallet': wallet_address}), 200
        
        return jsonify({'error': 'User not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== GROUP MANAGEMENT ====================

@app.route('/groups/create', methods=['POST'])
def create_group():
    """Create a new expense group"""
    try:
        data = request.get_json()
        group_name = data.get('group_name')
        user_id = data.get('user_id')
        group_rules = data.get('rules', {})
        
        if not group_name or not user_id:
            return jsonify({'error': 'Group name and user ID required'}), 400
        
        group_id = str(uuid.uuid4())
        groups_db[group_id] = {
            'id': group_id,
            'name': group_name,
            'creator': user_id,
            'members': [user_id],
            'rules': group_rules,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return jsonify({'message': 'Group created', 'group_id': group_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/groups/<group_id>/members', methods=['POST'])
def add_group_member(group_id):
    """Add member to group"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if group_id not in groups_db:
            return jsonify({'error': 'Group not found'}), 404
        
        if user_id not in groups_db[group_id]['members']:
            groups_db[group_id]['members'].append(user_id)
        
        return jsonify({'message': 'Member added', 'members': groups_db[group_id]['members']}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    """Get group details"""
    if group_id not in groups_db:
        return jsonify({'error': 'Group not found'}), 404
    
    return jsonify(groups_db[group_id]), 200


# ==================== EXPENSE MANAGEMENT ====================

@app.route('/expenses/add', methods=['POST'])
def add_expense():
    """Add expense to a group"""
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        paid_by = data.get('paid_by')
        amount = data.get('amount')
        description = data.get('description')
        split_among = data.get('split_among', [])
        
        if not all([group_id, paid_by, amount]):
            return jsonify({'error': 'Group ID, paid_by, and amount required'}), 400
        
        if group_id not in groups_db:
            return jsonify({'error': 'Group not found'}), 404
        
        expense_id = str(uuid.uuid4())
        expenses_db[expense_id] = {
            'id': expense_id,
            'group_id': group_id,
            'paid_by': paid_by,
            'amount': amount,
            'description': description,
            'split_among': split_among if split_among else groups_db[group_id]['members'],
            'created_at': datetime.now().isoformat(),
            'settled': False
        }
        
        return jsonify({'message': 'Expense added', 'expense_id': expense_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/expenses/<group_id>', methods=['GET'])
def get_expenses(group_id):
    """Get all expenses for a group"""
    if group_id not in groups_db:
        return jsonify({'error': 'Group not found'}), 404
    
    group_expenses = [exp for exp in expenses_db.values() if exp['group_id'] == group_id]
    return jsonify({'expenses': group_expenses}), 200


# ==================== TEX SETTLEMENT ALGORITHM ====================

def calculate_tex_settlement(group_id: str) -> List[Dict]:
    """Calculate minimum payments using TEX algorithm"""
    group_expenses = [exp for exp in expenses_db.values() if exp['group_id'] == group_id]
    members = groups_db[group_id]['members']
    
    balances = {member: 0 for member in members}
    
    # Calculate who owes whom
    for expense in group_expenses:
        if expense['settled']:
            continue
        
        amount_per_person = expense['amount'] / len(expense['split_among'])
        
        # Payer gets credit
        balances[expense['paid_by']] += expense['amount']
        
        # Each person in split owes
        for person in expense['split_among']:
            balances[person] -= amount_per_person
    
    # Generate settlement transactions (minimum payment algorithm)
    settlements = []
    positive = [(k, v) for k, v in balances.items() if v > 0]
    negative = [(k, v) for k, v in balances.items() if v < 0]
    
    for debtor, debt_amount in negative:
        for creditor, credit_amount in positive:
            if debt_amount == 0:
                break
            
            settlement_amount = min(abs(debt_amount), credit_amount)
            settlements.append({
                'from': debtor,
                'to': creditor,
                'amount': settlement_amount
            })
            
            debt_amount -= settlement_amount
            positive[positive.index((creditor, credit_amount))] = (creditor, credit_amount - settlement_amount)
    
    return settlements


@app.route('/settlements/calculate', methods=['POST'])
def calculate_settlement():
    """Calculate settlements for a group using TEX"""
    try:
        data = request.get_json()
        group_id = data.get('group_id')
        
        if group_id not in groups_db:
            return jsonify({'error': 'Group not found'}), 404
        
        settlements = calculate_tex_settlement(group_id)
        
        settlement_id = str(uuid.uuid4())
        settlements_db[settlement_id] = {
            'id': settlement_id,
            'group_id': group_id,
            'settlements': settlements,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        return jsonify({
            'settlement_id': settlement_id,
            'message': 'Settlement calculated',
            'settlements': settlements
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== RISK SCORING ====================

@app.route('/risk-score/<user_id>', methods=['GET'])
def get_risk_score(user_id):
    """Get freeloader risk score for a user"""
    try:
        if user_id in risk_scores_db:
            return jsonify(risk_scores_db[user_id]), 200
        
        # Calculate risk score
        late_payments = 0
        repeated_reminders = 0
        ignored_settlements = 0
        
        # Analyze user behavior (from expenses and settlements)
        score = (late_payments * 30) + (repeated_reminders * 40) + (ignored_settlements * 30)
        score = min(score, 100)  # Cap at 100
        
        risk_obj = {
            'user_id': user_id,
            'risk_score': score,
            'factors': {
                'late_payments': late_payments,
                'repeated_reminders': repeated_reminders,
                'ignored_settlements': ignored_settlements
            },
            'updated_at': datetime.now().isoformat()
        }
        
        risk_scores_db[user_id] = risk_obj
        return jsonify(risk_obj), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== WARNING SYSTEM ====================

@app.route('/warnings/apply', methods=['POST'])
def apply_warning():
    """Apply warning to user based on risk score"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        group_id = data.get('group_id')
        
        if not user_id or not group_id:
            return jsonify({'error': 'User ID and group ID required'}), 400
        
        # Get risk score
        risk_score = get_risk_score(user_id)
        score_data = risk_score.json if hasattr(risk_score, 'json') else risk_score
        score = score_data.get('risk_score', 0) if isinstance(score_data, dict) else 0
        
        # Determine warning level
        if score < 30:
            warning_level = 1
            message = "Friendly reminder to settle your dues"
        elif score < 70:
            warning_level = 2
            message = "Limited participation in next settlement cycle"
        else:
            warning_level = 3
            message = "Excluded from this settlement cycle"
        
        return jsonify({
            'user_id': user_id,
            'warning_level': warning_level,
            'message': message,
            'risk_score': score
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== BLOCKCHAIN SETTLEMENT ====================

@app.route('/settlements/execute', methods=['POST'])
def execute_blockchain_settlement():
    """Execute settlement on Algorand blockchain"""
    try:
        data = request.get_json()
        settlement_id = data.get('settlement_id')
        
        if settlement_id not in settlements_db:
            return jsonify({'error': 'Settlement not found'}), 404
        
        settlement = settlements_db[settlement_id]
        
        # Mark as executed
        settlement['status'] = 'executed'
        settlement['executed_at'] = datetime.now().isoformat()
        settlement['blockchain_txns'] = []
        
        # In production, here you'd call Algorand SDK
        for tx in settlement['settlements']:
            blockchain_tx = {
                'from': tx['from'],
                'to': tx['to'],
                'amount': tx['amount'],
                'txn_id': str(uuid.uuid4()),
                'status': 'confirmed'
            }
            settlement['blockchain_txns'].append(blockchain_tx)
        
        # Mark expenses as settled
        for expense in expenses_db.values():
            if expense['group_id'] == settlement['group_id']:
                expense['settled'] = True
        
        return jsonify({
            'message': 'Settlement executed on blockchain',
            'settlement': settlement
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== REPORTING ====================

@app.route('/report/<settlement_id>', methods=['GET'])
def get_settlement_report(settlement_id):
    """Get explainable AI report for settlement"""
    try:
        if settlement_id not in settlements_db:
            return jsonify({'error': 'Settlement not found'}), 404
        
        settlement = settlements_db[settlement_id]
        group_id = settlement['group_id']
        
        # Get all group expenses
        group_expenses = [exp for exp in expenses_db.values() if exp['group_id'] == group_id]
        
        report = {
            'settlement_id': settlement_id,
            'group_id': group_id,
            'summary': {
                'total_expenses': sum(exp['amount'] for exp in group_expenses),
                'transactions_needed': len(settlement['settlements']),
                'status': settlement['status']
            },
            'transactions': settlement['settlements'],
            'breakdown': {
                'who_paid': {},
                'who_delayed': [],
                'actions_taken': []
            },
            'generated_at': datetime.now().isoformat()
        }
        
        # Calculate who paid what
        for expense in group_expenses:
            if expense['paid_by'] not in report['breakdown']['who_paid']:
                report['breakdown']['who_paid'][expense['paid_by']] = 0
            report['breakdown']['who_paid'][expense['paid_by']] += expense['amount']
        
        return jsonify(report), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ROOT & HEALTH ====================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API documentation"""
    return jsonify({
        'message': 'Expense Settlement API - Powered by LangGraph & Algorand',
        'version': '1.0',
        'base_url': 'http://127.0.0.1:5000',
        'endpoints': {
            'auth': [
                'POST /auth/login',
                'POST /auth/connect-wallet'
            ],
            'groups': [
                'POST /groups/create',
                'POST /groups/<group_id>/members',
                'GET /groups/<group_id>'
            ],
            'expenses': [
                'POST /expenses/add',
                'GET /expenses/<group_id>'
            ],
            'settlements': [
                'POST /settlements/calculate',
                'POST /settlements/execute',
                'GET /report/<settlement_id>'
            ],
            'risk': [
                'GET /risk-score/<user_id>',
                'POST /warnings/apply'
            ],
            'health': [
                'GET /health'
            ]
        }
    }), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
