import pytest


@pytest.fixture
def greeting_quiz():
    return [
        {
            'id': '1',
            'question': 'Indicate your gender.',
            'answer_validation': {
                'type': 'variants',
                'variants': {
                    'm': ['m', 'male'],
                    'f': ['f', 'female'],
                },
            },
        },
        {
            'id': '2',
            'question': 'How old are you?',
            'answer_validation': {
                'type': 'interval',
                'interval': [0, 100],
            },
        },
        {
            'id': '3',
            'question': 'Tell us about your hobbies.',
            'answer_validation': {
                'type': 'text',
            },
        },
    ]
