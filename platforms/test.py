def add_comma(number):
    number_str = str(number).split('.')[0]
    decimal_str = None
    if '.' in str(number):
        decimal_str = str(number).split('.')[1]
    if len(number_str) <= 3:
        if decimal_str:
            return number_str + '.' + decimal_str
        return number_str
    reversed_str = number_str[::-1]
    comma_added_str = ",".join([reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)])
    comma_added_str = comma_added_str[::-1]
    if decimal_str:
        comma_added_str += '.' + decimal_str
    return comma_added_str

print(add_comma(123456789))
print(round(123456789.88,2))