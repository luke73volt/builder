from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)

            user_roles = [role.name for role in current_user.roles]
            if not any(role in user_roles for role in roles):
                abort(403)

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
