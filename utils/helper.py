from datetime import datetime

def format_remaining_time(expires_at_str: str) -> str:
    try:
        expires_at = datetime.fromisoformat(expires_at_str)
        now = datetime.now()
        remaining = expires_at - now
        
        if remaining.total_seconds() <= 0:
            return "0 kun 0 soat 0 daqiqa"
            
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        
        return f"{days} kun {hours} soat {minutes} daqiqa"
    except Exception:
        return "Noma'lum"

