from flask_wtf import FlaskForm


def wtforms_debug(form: FlaskForm):
    print("#################################################")
    for fieldName, errorMessages in form.errors.items():
        print("Campo: " + fieldName)
        print("Erros:")
        for err in errorMessages:
            print(err)
        print("----------------------------------------")
