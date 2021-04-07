from user import models


def test_models_insert():
    models.insert('michol', 'michol@gmail.com', '1234','male')

def test_models_find_by_email_and_password():
    result = models.findby_email_and_password('michol@gmail.com', '1234')
    print(result)

#test_models_insert()
test_models_find_by_email_and_password()