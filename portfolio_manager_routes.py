from flask import Blueprint
from portfolio import get_portfolio_summary

portfolio_manager_bp = Blueprint("portfolio_manager", __name__)