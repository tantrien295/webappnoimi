def format_number(value):
    """
    Định dạng số với dấu phân cách hàng nghìn
    Ví dụ: 1000000 -> 1.000.000
    """
    try:
        value = int(value) if value is not None else 0
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return "0"
