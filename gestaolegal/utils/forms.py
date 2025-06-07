from wtforms import FloatField
from wtforms.validators import DataRequired, InputRequired, Optional


# TODO: Organizar essa bagunça de RequiredIf(fui fazendo modificações e criando novos a medida que precisei k k k)
class RequiredIf(DataRequired):
    # Validator which makes a field required if another field is set and has a truthy value.

    # Sources:
    #    - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
    #    - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
    #    - https://gist.github.com/devxoul/7638142#file-wtf_required_if-py

    field_flags = ("requiredif",)

    def __init__(self, message=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            if other_field.data == data and not field.data:
                obrigatorio = True
            else:
                obrigatorio = False
                break
        if obrigatorio:
            DataRequired.__call__(self, form, field)
        else:
            Optional()(form, field)


class RequiredIf_InputRequired(DataRequired):
    # Validator which makes a field required if another field is set and has a truthy value.

    # Sources:
    #    - http://wtforms.simplecodes.com/docs/1.0.1/validators.html
    #    - http://stackoverflow.com/questions/8463209/how-to-make-a-field-conditionally-optional-in-wtforms
    #    - https://gist.github.com/devxoul/7638142#file-wtf_required_if-py

    field_flags = ("requiredif",)

    def __init__(self, message=None, *args, **kwargs):
        super(RequiredIf).__init__()
        self.message = message
        self.conditions = kwargs

    # field is requiring that name field in the form is data value in the form
    def __call__(self, form, field):
        for name, data in self.conditions.items():
            other_field = form[name]
            if other_field is None:
                raise Exception('no field named "%s" in form' % name)
            if other_field.data == data and not field.data:
                InputRequired.__call__(self, form, field)
            Optional()(form, field)


class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid float value"))
