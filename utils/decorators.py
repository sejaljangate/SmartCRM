from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(view_func):
    """
    Use on any route that only an admin should access.
    Employees get a 403 Forbidden instead of the page.
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped