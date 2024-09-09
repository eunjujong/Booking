from datetime import datetime, timedelta

def generate_weekly_dates():
    days = []
    days_str = []
    
    # cronjob runs on Saturday evening UDT
    today = datetime.today()
    
    thursday = today + timedelta((3 - today.weekday()) % 7)
    friday = today + timedelta((4 - today.weekday()) % 7)
    saturday = today + timedelta(days=7)
    
    days.append(thursday.strftime('%Y-%m-%d'))
    days_str.append(thursday.strftime('%A'))
    days.append(friday.strftime('%Y-%m-%d'))
    days_str.append(friday.strftime('%A'))
    days.append(saturday.strftime('%Y-%m-%d'))
    days_str.append(saturday.strftime('%A'))
    
    return days, days_str

# testing
# def generate_weekly_dates():
#     today = datetime.today()
#     tomorrow = today + timedelta(days=1)
    
#     return [tomorrow.strftime('%Y-%m-%d')], [tomorrow.strftime('%A')]
