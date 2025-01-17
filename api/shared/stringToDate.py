
"""
THe goal: convert date sent from the front-ent,
as: 'Thu Dec 05 2024 02:00:00 GMT+0200 (Central Africa Time)',
into: [2024, 12, 5]
"""


months = {
    'Jan':1,
    'Feb':2,
    'Mar':3,
    'Apr':4,
    'May':5,
    'Jun':6,
    'Jul':7,
    'Aug':8,
    'Sep':9,
    'Oct':10,
    'Nov':11,
    'Dec':12
}
date = 'Thu Dec 05 2024 02:00:00 GMT+0200 (Central Africa Time)'
def stringToDate(date:str)->list:
    date_list = str(date).split('-')
    print(f"Date list: {date_list}; from {date}")
    year = int(date_list[0])
    month = 1
    if not (months.get(date_list[1])): # Date of this form: '2024-12-16'
        month_ = date_list[1]
        if month_[0] == '0':
            month = month_[1]
    else:
        month = int(months.get(date_list[1]))
    day = int(date_list[2])

    return [year, month, day]

def shortStr2Date(date:str)->list:
    """
    Date of this form: '2024-12-16'
    """
    date_list = date.split('-')
    return [int(date_list[0]), int(date_list[1]),\
            int(date_list[2])]