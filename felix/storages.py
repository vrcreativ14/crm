from urllib import parse as urlparse

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from storages.backends.azure_storage import AzureStorage


class PublicAzureStorage(AzureStorage):
    account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = 'container-public'


class PrivateAzureStorage(AzureStorage):
    account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
    account_key = settings.AZURE_STORAGE_KEY
    azure_container = 'container-private'
    expiration_secs = 3600


class PublicS3Storage(S3Boto3Storage):
    auto_create_bucket = settings.DEBUG  # So we don't have to go and create the bucket manually when developing

    bucket_name = settings.PUBLIC_S3_BUCKET
    default_acl = 'public-read'
    bucket_acl = default_acl
    signature_version = 's3v4'

    custom_domain = settings.PUBLIC_BUCKET_CDN_DOMAIN

    querystring_auth = False
    gzip = True

    def url(self, name, parameters=None, expire=None):
        original_url = super().url(name, parameters, expire)

        parsed_url = urlparse.urlsplit(original_url)
        parsed_qs = urlparse.parse_qsl(parsed_url.query)
        parsed_qs.append(('build', settings.ASSET_ID))
        qs_with_build = urlparse.urlencode(parsed_qs, True)

        url_with_build_id = urlparse.urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                                 qs_with_build, parsed_url.fragment))
        return url_with_build_id


class PrivateS3Storage(S3Boto3Storage):
    auto_create_bucket = settings.DEBUG

    bucket_name = settings.PRIVATE_S3_BUCKET
    default_acl = 'private'
    bucket_acl = default_acl
    signature_version = 's3v4'

    querystring_auth = True
    querystring_expire = 604800  # 7 Days because that's the max with the new signature version
    gzip = True
