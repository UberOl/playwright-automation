def test_get_answer(ultimate_answer):
    assert 42 == ultimate_answer

def test_get_new_unswer(new_answer):
    assert 43 == new_answer

def test_get_answers(ultimate_answer, new_answer):
    assert 42 + 43 == ultimate_answer + new_answer

def test_native(request):
    assert 'test.py' == request.fspath.basename