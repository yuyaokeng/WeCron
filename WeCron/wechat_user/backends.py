#coding: utf-8
from __future__ import unicode_literals, absolute_import
import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from wechatpy import WeChatOAuth, WeChatOAuthException

logger = logging.getLogger(__name__)
UserModel = get_user_model()


def make_guest(**kw):
    u = UserModel(**kw)
    u.subscribe = False
    u.save = lambda **kw: 1
    return u


class WechatBackend(object):

    def authenticate(self, code=None, redirect_uri=None, state=None):
        oauth_client = WeChatOAuth(
            app_id=settings.WX_APPID,
            secret=settings.WX_APPSECRET,
            redirect_uri=redirect_uri,
            scope='snsapi_base',
            state=state
        )

        try:
            oauth_client.fetch_access_token(code)
            return UserModel.objects.get(pk=oauth_client.open_id)
        except WeChatOAuthException as e:
            logger.warning('Failed to get access token due to %s', e)
            return None
        except UserModel.DoesNotExist:
            return make_guest(pk=oauth_client.open_id, nickname=oauth_client.open_id)

    def get_user(self, open_id):
        try:
            return UserModel.objects.get(pk=open_id)
        except UserModel.DoesNotExist:
            return make_guest(pk=open_id, nickname=open_id)
