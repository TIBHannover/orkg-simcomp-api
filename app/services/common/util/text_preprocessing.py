# -*- coding: utf-8 -*-
from stop_words import get_stop_words


def get_english_stop_words():
    return _get_stop_words("en")


def _get_stop_words(language):
    return get_stop_words(language)


def clean_labels(labels):
    stop_words = get_english_stop_words()
    return [" ".join([w for w in val.lower().split(" ") if w not in stop_words]) for val in labels]
