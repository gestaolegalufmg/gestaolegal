from wtforms import FloatField
from wtforms.validators import ValidationError


class RequiredIf:
    """
    Custom validator that makes a field required based on another field's value.
    Modern replacement for the old RequiredIf validator.
    """

    def __init__(self, fieldname, value=None, message=None, **kwargs):
        self.fieldname = fieldname
        self.value = value
        self.message = message
        self.kwargs = kwargs

    def __call__(self, form, field):
        other_field = form._fields.get(self.fieldname)
        if other_field is None:
            raise Exception(f'No field named "{self.fieldname}" in form')

        # Check if multiple conditions need to be met
        conditions_met = True

        # Check main fieldname condition
        if self.value is not None:
            if other_field.data != self.value:
                conditions_met = False
        else:
            if not other_field.data:
                conditions_met = False

        # Check additional kwargs conditions
        for kwarg_fieldname, kwarg_value in self.kwargs.items():
            kwarg_field = form._fields.get(kwarg_fieldname)
            if kwarg_field and kwarg_field.data != kwarg_value:
                conditions_met = False
                break

        if conditions_met and not field.data:
            message = self.message or "This field is required."
            raise ValidationError(message)


class RequiredIfInputRequired(RequiredIf):
    """
    Similar to RequiredIf but for numeric fields that need InputRequired behavior.
    """

    def __call__(self, form, field):
        other_field = form._fields.get(self.fieldname)
        if other_field is None:
            raise Exception(f'No field named "{self.fieldname}" in form')

        if other_field.data == self.value and field.data is None:
            message = self.message or "This field is required."
            raise ValidationError(message)


class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid float value"))
