# -*- coding: utf-8 -*-
import logging
from vkaudiotoken import CommonParams, TokenReceiverOfficial, supported_clients, TokenException, TwoFAHelper
from . import wxUI

log = logging.getLogger("authenticator.official")

class AuthenticationError(Exception): pass

def login(user, password):
    """ Generates authentication workflow at VK servers. """
    log.info("Authenticating user account.")
    access_token = None
    try:
        params = CommonParams(supported_clients.VK_OFFICIAL.user_agent)
        receiver = TokenReceiverOfficial(user, password, params, "GET_CODE")
        access_token = receiver.get_token()["access_token"]
        log.debug("got a valid access token for {}".format(user))
    except TokenException as err:
        if err.code == TokenException.TWOFA_REQ and 'validation_sid' in err.extra:
            log.debug("User requires two factor verification. Calling methods to send an SMS...")
            try:
                TwoFAHelper(params).validate_phone(err.extra['validation_sid'])
            except TokenException as err:
                if err.code == TokenException.TWOFA_ERR:
                    wxUI.two_auth_limit()
                    raise AuthenticationError("Error authentication two factor auth.")
            code, remember = wxUI.two_factor_auth()
            receiver = TokenReceiverOfficial(user, password, params, code)
            access_token = receiver.get_token()["access_token"]
    return access_token
