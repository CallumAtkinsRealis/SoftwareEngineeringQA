from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class SpecialCharacterValidator:
    def validate(self, password, user=None):
            if len(password) < 8 or len(password) > 20:
                raise ValidationError(
                    _("Password must be between 8-20 characters."),
                    code='password_too_short_or_long',
                )
            if not any(char in '!@#$%^&*()_+' for char in password):
                raise ValidationError(
                    _("Password must include at least one special character: !@#$%^&*()_+"),
                    code='password_no_special',
                )

    def get_help_text(self):
        return _("Your password must be between 8-20 characters and include at least one special character: !@#$%^&*()_+")