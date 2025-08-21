import sys
sys.dont_write_bytecode = True

from datetime import datetime, timedelta

def get_expiry_weekly_current_week():
    """
    Returns the expiry date for the current week.
    The expiry is the upcoming Thursday. If today is Thursday, it's today.
    If today is past Thursday, it's next week's Thursday.
    """
    today = datetime.now()
    days_until_thursday = (3 - today.weekday() + 7) % 7
    expiry_date = today + timedelta(days=days_until_thursday)
    return expiry_date.date()


if __name__ == "__main__":
    expiry_date = get_expiry_weekly_current_week()
    print(f"The current weekly expiry date is: {expiry_date}")