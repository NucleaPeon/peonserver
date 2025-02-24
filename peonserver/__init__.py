import os
from formencode import validators, Schema, api
import functools


__all__ = ["HERE", "Validator", "NewsletterValidator", "EmailValidator"]

HERE = os.path.abspath(os.path.dirname(__file__))

### DECORATORS ###

def args_to_dict(params):
    p = {}
    for k, v in params.items():
        p[k] = v[0].decode("utf-8")
    return p

class Validator():
    def __init__(self, validator, *args, **kwargs):
        self.validator = validator

    def __call__(self, func, *args, **kwargs):
        v = self.validator
        def wrapper(self, *args, **kwargs):
            # Coerce to dict
            params = args_to_dict(self.request.arguments)
            # Coerce to proper values
            try:
                params = v.to_python(params)
                return func(self, params, False, *args, **kwargs)
            except api.Invalid as Invalid:
                return func(self, dict(error=str(Invalid)), True,
                         *args, **kwargs)
        return wrapper


### VALIDATORS ###

class EmailValidator(Schema):
    allow_extra_fields = True

    email = validators.Email(not_empty=True, min=5, max=256, strip=True)

class NewsletterValidator(EmailValidator):
    allow_extra_fields = True
    filter_extra_fields = True

    name  = validators.UnicodeString(min=2, max=256, not_empty=True, strip=True)


