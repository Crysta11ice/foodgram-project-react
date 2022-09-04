from base64 import b64decode
from imghdr import what
from uuid import uuid4

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField
from six import string_types

BASE64 = ";base64,"


class Base64ImageField(ImageField):
    def to_internal_value(self, data):

        if isinstance(data, string_types):
            if "data:" in data and BASE64 in data:
                header, data = data.split(BASE64)
            try:
                result_file = b64decode(data)
            except TypeError:
                self.fail("Неверный формат изображения!")

            file_name = str(uuid4())[:12]
            file_extension = self.get_file_extension(file_name, result_file)
            result_filename = "%s.%s" % (file_name, file_extension)
            data = ContentFile(result_file, name=result_filename)

        return super().to_internal_value(data)

    def get_file_extension(self, file_name, result_file):
        extension = what(file_name, result_file)
        return "jpg" if extension == "jpeg" else extension
