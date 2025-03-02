import threading
from datetime import datetime
import json
from . import socketio

class AlertSystem:
    def __init__(self):
        self.alerts = []
        self.alert_rules = {
            'high_traffic': 1000000,  # 1MB/s
            'suspicious_ports': [22, 3389, 445],
            'max_connections': 100
        }

    def check_traffic_threshold(self, bytes_sent, bytes_recv):
        total_traffic = bytes_sent + bytes_recv
        if total_traffic > self.alert_rules['high_traffic']:
            self.create_alert('High Traffic Alert', 
                            f'Traffic exceeded threshold: {total_traffic} bytes')

    def check_suspicious_connections(self, connections):
        for conn in connections:
            try:
                port = int(conn['remote_addr'].split(':')[1])
                if port in self.alert_rules['suspicious_ports']:
                    self.create_alert('Suspicious Port Activity',
                                    f'Connection detected on port {port}')
            except:
                continue

    def create_alert(self, title, message):
        alert = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'message': message
        }
        self.alerts.append(alert)
        socketio.emit('new_alert', alert)   