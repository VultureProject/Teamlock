
REDIS_HOST = "<REDIS_HOST>"
REDIS_PORT = 6379

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '<DATABASE_NAME>',
        'HOST': '<DATABASE_HOST>',
        'PORT': 5432,
        'USER': '<DATABASE_USER>',
        'PASSWORD': '<DATABASE_PASSWORD>'
    }
}


PUBLIC_URI = "<PUBLIC_URI>"

JWT_EXPIRATION = 300
PROXY = {
    "http": "",
    "https": "",
    "ftp": ""
}
