import pytest


def test_unwrap():
    # NEEDS: pip install phonenumbers
    # Otherwise, this test is skipped.

    import phonenumbers

    from onto.models.base import Serializable

    class PhoneNumber(Serializable):

        class Meta:
            unwrap = 'formatted_number'

        from onto.attrs import attrs
        formatted_number = attrs.string.optional
        number_object: phonenumbers.PhoneNumber = attrs.internal.optional
        with attrs.easy_init(lambda self: None) as attrs:
            country_code: str = attrs.optional
            national_number: str = attrs.optional
            extension: str = attrs.optional
            raw_input: str = attrs.optional

        @formatted_number.getter
        def formatted_number(self):
            return phonenumbers.format_number(
                self.number_object,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )

        @formatted_number.setter
        def formatted_number(self, formatted_number):
            self._attrs.number_object = phonenumbers.parse(
                formatted_number
            )

        @number_object.getter
        def number_object(self):
            if not hasattr(self._attrs, 'number_object'):
                return phonenumbers.PhoneNumber(
                    country_code=self.country_code,
                    national_number=self.national_number,
                    extension=self.extension,
                    raw_input=self.raw_input,
                )
            else:
                return self._attrs.number_object

    number = PhoneNumber.new(
        country_code='+86',
        national_number='13212345678'
    )

    assert number.formatted_number == '+86 132 1234 5678'
    assert number.to_dict() == '+86 132 1234 5678'
    assert PhoneNumber.from_dict('+86 132 1234 5678').formatted_number == '+86 132 1234 5678'
