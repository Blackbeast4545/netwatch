from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required
from .network_monitor import NetworkMonitor
from datetime import datetime

main = Blueprint('main', __name__)
network_monitor = NetworkMonitor()  # Create a single instance

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    if not network_monitor.running:
        network_monitor.start()  # Start monitoring if not already running
    return render_template('dashboard.html', datetime=datetime)

@main.route('/filter', methods=['POST'])
@login_required
def apply_filter():
    filter_data = request.json
    filtered_results = {
        'protocol': filter_data.get('protocol'),
        'ip': filter_data.get('ip'),
        'port': filter_data.get('port'),
        'start_time': filter_data.get('start_time'),
        'end_time': filter_data.get('end_time')
    }
    return jsonify(filtered_results)

@main.route('/export', methods=['POST'])
@login_required
def export_data():
    export_type = request.json.get('type', 'csv')
    if export_type == 'csv':
        return network_monitor.export_statistics()
    return jsonify({'status': 'error', 'message': 'Invalid export type'}) 