
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
    date_list = date.split
    year = int(date_list[3])
    month = int(months.get(date_list[1]))
    day = int(date_list[2])

    return [year, month, day]