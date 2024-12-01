months = ["January", "February", "March", "April", "May", "June", 
          "July", "August", "September", "October", "November", "December"]

def GetMonth(month):
    return months.index(month) + 1 if month else None


def GetDataLevel(map_type):
    return "hex" if map_type == "Hexagons" else "region"


def GetRollingWindow(period):
    return int(period.split(" ")[0])


def GetMinYear(min_year, rolling_window):
    if rolling_window != 1:
        min_year += rolling_window
    return min_year