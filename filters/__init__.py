from flask import Blueprint
from . import number_filters
from . import string_filters

def init_app(app):
    # Đăng ký các filter từ number_filters
    app.jinja_env.filters['format_number'] = number_filters.format_number
    # Đăng ký các filter từ string_filters
    app.jinja_env.filters['split'] = string_filters.split_string
