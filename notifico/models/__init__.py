# -*- coding: utf8 -*-
from sqlalchemy import func
from sqlalchemy.ext.hybrid import Comparator


class CaseInsensitiveValue(Comparator):
    def __init__(self, key, value):
        self.key = key

        if isinstance(value, basestring):
            self._value = value.lower()
        elif isinstance(value, CaseInsensitiveValue):
            self._value = value._value
        else:
            self._value = func.lower(value)

    def operate(self, op, other):
        if not isinstance(other, CaseInsensitiveValue):
            other = CaseInsensitiveValue(self.key, other)
        return op(self._value, other._value)

    def __clause_element__(self):
        return self._value

    def __str__(self):
        return str(self._value)

    @property
    def _value(self):
        return getattr(self, self.key)

    @_value.setter
    def _value(self, value):
        setattr(self, self.key, value)
