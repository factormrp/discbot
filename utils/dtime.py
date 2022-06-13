from typing import Union
import datetime

def get_today(string=False):
    today = datetime.datetime.today()
    if string:
        return str(today)[:-7]
    return today

def is_upcoming(check_date:Union[datetime.date,str],days:int,string=False,ref_date=datetime.date.today()) -> bool:
    """
    Checks whether `date` will occur in the next few `days` from current date.

    The `ref_date`, if not given, is the current date. Note that `date` should be formatted as 'YYYY-MM-DD'.
    """
    # convert date to datetime
    if string:
        cdate = datetime.date.fromisoformat(check_date)
    else:
        cdate = check_date

    # perform datetime arithmetic
    diff:datetime.timedelta = cdate - ref_date
    
    # Check difference to determine if cdate is upcoming
    if diff.days > days or diff.days < 0:
        return False
    return True 
