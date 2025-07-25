from datetime import datetime, timedelta

def get_expiry_weekly_next_week():
    """
    Returns the expiry date for the next week.
    The expiry is set to the last Thursday of the next week.
    """
    today = datetime.now()

    days_until_thursday = (3 - today.weekday()) % 7 + 7

    if days_until_thursday == 0:
        return today.date() + timedelta(weeks=1)


    next_thursday = today + timedelta(days=days_until_thursday)
    return next_thursday.date()


if __name__ == "__main__":
    expiry_date = get_expiry_weekly_next_week()
    print(f"The expiry date for the next week is: {expiry_date}")


