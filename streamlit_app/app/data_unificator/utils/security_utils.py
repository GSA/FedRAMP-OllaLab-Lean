# utils/security_utils.py

def sanitize_data(df):
    """
    Sanitize data to prevent code execution, memory overflow, and other security issues.
    """
    # Remove potentially dangerous content
    df = df.applymap(lambda x: str(x).replace('=', '').replace('@', '').replace('+', '') if isinstance(x, str) else x)
    # Limit string lengths to prevent memory overflow
    df = df.applymap(lambda x: x[:1000] if isinstance(x, str) else x)
    return df
