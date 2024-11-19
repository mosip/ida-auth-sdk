import string
import secrets
import logging
import sys
import traceback
import urllib
from datetime import datetime
from typing import Literal, Optional
from .model import MOSIPAuthRequest, DemographicsModel, MOSIPEncryptAuthRequest
from .utils import CryptoUtility, RestUtility
from .exceptions import AuthenticatorException, Errors

type AuthController = Literal['ekyc', 'auth']
type AuthControllerWay = Literal['demo', 'kyc', 'otp']

class MOSIPAuthenticator:
    def __init__(self, config_obj, logger=None, **kwargs):
        if not logger:
            self.logger = self._init_logger(config_obj.logging.log_file_path)
        else:
            self.logger = logger

        self.auth_rest_util = RestUtility(config_obj.mosip_auth_server.ida_auth_url, config_obj.mosip_auth.authorization_header_constant)
        self.crypto_util = CryptoUtility(config_obj.crypto_encrypt, config_obj.crypto_signature)

        self.auth_domain_scheme = config_obj.mosip_auth_server.ida_auth_domain_uri

        self.partner_misp_lk =  str(config_obj.mosip_auth.partner_misp_lk)
        self.partner_id = str(config_obj.mosip_auth.partner_id)
        self.partner_apikey = str(config_obj.mosip_auth.partner_apikey)

        self.ida_auth_version = config_obj.mosip_auth.ida_auth_version
        self.ida_auth_request_id_by_controller = {
            'demo': config_obj.mosip_auth.ida_auth_request_demo_id,
            'otp': config_obj.mosip_auth.ida_auth_request_otp_id,
            'kyc': config_obj.mosip_auth.ida_auth_request_kyc_id,
        }
        self.ida_auth_env = config_obj.mosip_auth.ida_auth_env
        self.timestamp_format = config_obj.mosip_auth.timestamp_format
        self.authorization_header_constant = config_obj.mosip_auth.authorization_header_constant

    @staticmethod
    def _init_logger(filename):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        fileHandler = logging.FileHandler(filename)
        streamHandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
        logger.addHandler(fileHandler)
        return

    def _get_default_auth_request(self, controller: AuthControllerWay, **, timestamp=None, individual_id='', txn_id=''):
        _timestamp = timestamp or datetime.utcnow()
        timestamp_str = _timestamp.strftime(self.timestamp_format) + timestamp.strftime('.%f')[0:4] + 'Z'
        transaction_id = txn_id or ''.join([secrets.choice(string.digits) for _ in range(10)])
        id = self.ida_auth_request_id_by_controller.get(controller, '')
        if not id:
            err_msg = Errors.AUT_CRY_005.value.format(
                repr(controller),
                ' | '.join(self.ida_auth_request_id_by_controller.keys())
            )
            self.logger.error('Received Auth Request for demographic.')
            raise AuthenticatorException(Errors.AUT_CRY_005.name, err_msg)
        return MOSIPAuthRequest(
            id = id,
            version = self.ida_auth_version,
            env = self.ida_auth_env,
            domainUri = self.auth_domain_scheme,
            specVersion = self.ida_auth_version,
            consentObtained = True,
            metadata = {},
            thumbprint = self.crypto_util.enc_cert_thumbprint,
            individualId = individual_id,
            transactionID = transaction_id,
            requestTime = timestamp_str,
            request = '',
            requestSessionKey = '',
            requestHMAC = '',
        )

    def authenticate(
            self,
            **,
            controller: AuthController,
            vid: str,
            demographic_data: DemographicsModel,
            otp_value: Optional[str]=None,
            biometrics: Optional[List[BiometricModel]]=None
    ):
        '''
        '''
        self.logger.info('Received Auth Request for demographic.')
        auth_request = self._get_default_auth_request(
            individual_id=vid,
        )
        auth_request.requestedAuth.demo = True
        auth_request.requestedAuth.otp = bool(otp_value)
        auth_request.requestedAuth.bio = bool(biometrics)
        request = MOSIPEncryptAuthRequest(
            timestamp = auth_request.requestTime,
            biometrics = [],
            demographics = demographic_data,
        )
        try:
            signature_header = {'Signature': self.crypto_util.sign_auth_request_data(full_request_json)}
            auth_request.request, auth_request.requestSessionKey, auth_request.requestHMAC = \
                self.crypto_util.encrypt_auth_data(request.json())
            path_params = '/'.join(
                map(
                    urllib.parse.quote,
                    ('kyc' if controller == 'ekyc' else 'auth',
                     self.partner_misp_lk, self.partner_id, self.partner_apikey)
                )
            )
            full_request_json = auth_request.json()
            response = self.auth_rest_util.post_request(path_params=path_params, data=full_request_json, additional_headers=signature_header)
            self.logger.info('Auth Request for Demographic Completed.')
            return response.text
        except:
            exp = traceback.format_exc()
            self.logger.error('Error Processing Auth Request. Error Message: {}'.format(exp))
            raise AuthenticatorException(Errors.AUT_BAS_001.name, Errors.AUT_BAS_001.value)
