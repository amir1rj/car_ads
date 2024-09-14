from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseUserManager(models.Manager):
    @classmethod
    def normalize_username(cls, username):
        """
        Normalize the username by lowercasing it.
        """
        username = username or ""
        if len(username) < 4:
            raise ValueError(_('نام کاربری باید شامل حداقل چهار کاراکتر باشد'))
        return username.lower()

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None):
        """
        Creates and saves a User with the given username and password.
        """
        if not phone_number:
            raise ValueError("شماره تلفن اجباری است")

        user = self.model(

            phone_number=phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_with_phone(self, data):
        """
        Creates and saves a User with the given username,phone number and password.
        """
        if not data["phone"]:
            raise ValueError("شماره تلفن اجباری است")
        if not data['username']:
            raise ValueError("نام کاربری اجباری است")
        user = self.model(

            phone_number=data['phone_number'], username=data['username'], verified=True, password=data['password']
        )

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(

            password=password,
            phone_number=phone_number,
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
