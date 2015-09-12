import requests

from recaptcha.client.captcha import displayhtml, submit as submit_recaptcha
from django.utils.translation import ugettext_lazy as _

from misago.conf import settings
from misago.core import forms


"""
Session flagging
"""
def session_already_passed_test(session):
    return session.get('passed_captcha')


def mark_session_as_passing(session):
    session['passed_captcha'] = True


def reset_session(session):
    session.pop('passed_captcha', None)


"""
Captcha tests
"""
def recaptcha_test(request):
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        'secret': settings.recaptcha_secret_key,
        'response': request.data.get('captcha'),
        'remoteip': request.user_ip
    })

    if r.status_code == 200:
        response_json = r.json()
        if not response_json.get('success'):
            raise forms.ValidationError(_("Please try again."))
    else:
        raise forms.ValidationError(_("Failed to contact reCAPTCHA API."))


def qacaptcha_test(request):
    answer = request.data.get('captcha', '').lower()
    for predefined_answer in settings.qa_answers.lower().splitlines():
        predefined_answer = predefined_answer.strip().lower()
        if answer == predefined_answer:
            break
    else:
        raise forms.ValidationError(_("Entered answer is incorrect."))


def nocaptcha_test(request):
    return # no captcha means no validation


CAPTCHA_TESTS = {
    're': recaptcha_test,
    'qa': qacaptcha_test,
    'no': nocaptcha_test,
}

def test_request(request):
    if not session_already_passed_test(request.session):
        # run test and if it didn't raise validation error,
        # mark session as passing so we don't troll uses anymore
        CAPTCHA_TESTS[settings.captcha_type](request)
        mark_session_as_passing(request.session)
