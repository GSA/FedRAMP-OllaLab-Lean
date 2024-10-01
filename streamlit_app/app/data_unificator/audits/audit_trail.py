# audits/audit_trail.py

from datetime import datetime
from data_unificator.config import ConfigManager

config_manager = ConfigManager()
audit_file = config_manager.get('audit_trail', 'audit_file', 'logs/data_unificator_audit.log')

def record_action(action):
    timestamp = datetime.now().isoformat()
    with open(audit_file, 'a') as f:
        f.write(f"{timestamp} - {action}\n")

