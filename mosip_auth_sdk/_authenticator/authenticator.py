import string
import secrets
import logging
import sys
import traceback
import urllib
from datetime import datetime
from typing import Literal, Optional, Dict, TypeAlias, List
from .model import MOSIPAuthRequest, DemographicsModel, MOSIPEncryptAuthRequest, BiometricModel
from .utils import CryptoUtility, RestUtility
from .exceptions import AuthenticatorException, Errors

AuthController: TypeAlias = Literal['kyc', 'auth']

class MOSIPAuthenticator:
    """
    Wrapper for the Mosip Authentication Service.

    MOSIP provides two authentication controllers:
    1. kyc-auth-controller:
       - Reference: https://mosip.github.io/documentation/1.2.0/authentication-service.html#tag/kyc-auth-controller
    2. auth-controller:
       - Reference: https://mosip.github.io/documentation/1.2.0/authentication-service.html#operation/authenticateIndividual

    These methods are exposed via the `kyc` and `auth` methods respectively.

    Methods:
        kyc(vid: str, demographic_data: DemographicsModel, otp_value: str = None, biometrics: list[BiometricModel] = None) -> Response:
            Wrapper for the kyc-auth-controller

        auth(vid: str, demographic_data: DemographicsModel, otp_value: Optional[str] = None, biometrics: Optional[List[BiometricModel]] = None) -> Response:
            Wrapper for the auth-controller

    Common Parameters for `auth`, `kyc`:
        vid (str): The unique VID  of the individual to authenticate.
        demographic_data (DemographicsModel): The demographic data for the individual.
        otp_value (Optional[str]): The One-Time Password (OTP) value, if applicable. Default is None.
        biometrics (Optional[List[BiometricModel]]): A list of biometric data models for the individual, if applicable. Default is None.

    Example:
    --------
    ```python
    from mosip_auth_sdk import MOSIPAuthenticator
    from mosip_auth_sdk.models import DemographicsModel, BiometricModel

    authenticator = MOSIPAuthenticator(config={
        # Your configuration settings go here.
        # Refer to tests/authenticator-config.toml for the required values.
    })

    # Refer the DemographicsModel, BiometricModel documentation to know
    # the exact arguments to be passed in there
    demographics_data = DemographicsModel()
    biometrics = [BiometricModel(), BiometricModel()]

    # Make a KYC request
    response = authenticator.kyc(
        vid='<some_vid>',
        demographic_data=demographics_data,
        otp_value='323',  # Optional
        biometrics=biometrics,  # Optional
    )
    ```
    """

    def __init__(self, *, config, logger=None):
        '''
        '''
        self._validate_config(config)
        if not logger:
            self.logger = self._init_logger(
                file_path=config.logging.log_file_path,
                level=config.logging.loglevel or logging.INFO,
                format=config.logging.log_format,
            )
        else:
            self.logger = logger

        self.auth_rest_util = RestUtility(config.mosip_auth_server.ida_auth_url, config.mosip_auth.authorization_header_constant, logger=self.logger)
        self.crypto_util = CryptoUtility(config.crypto_encrypt, config.crypto_signature)

        self.auth_domain_scheme = config.mosip_auth_server.ida_auth_domain_uri

        self.partner_misp_lk =  str(config.mosip_auth.partner_misp_lk)
        self.partner_id = str(config.mosip_auth.partner_id)
        self.partner_apikey = str(config.mosip_auth.partner_apikey)

        self.ida_auth_version = config.mosip_auth.ida_auth_version
        self.ida_auth_request_id_by_controller: Dict[AuthController, str]  = {
            'auth': config.mosip_auth.ida_auth_request_demo_id,
            'kyc': config.mosip_auth.ida_auth_request_kyc_id,
        }
        self.ida_auth_env = config.mosip_auth.ida_auth_env
        self.timestamp_format = config.mosip_auth.timestamp_format
        self.authorization_header_constant = config.mosip_auth.authorization_header_constant

    @staticmethod
    def _validate_config(config):
        if not config.mosip_auth_server.ida_auth_url:
            raise KeyError("Config should have 'ida_auth_url' set under [mosip_auth_server] section")
        if not config.mosip_auth_server.ida_auth_domain_uri:
            raise KeyError("Config should have 'ida_auth_domain_uri' set under [mosip_auth_server] section")

    @staticmethod
    def _init_logger(
            *,
            file_path,
            format,
            level):
        logger = logging.getLogger(file_path)
        logger.setLevel(level)
        fileHandler = logging.FileHandler(file_path)
        streamHandler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(format)
        streamHandler.setFormatter(formatter)
        fileHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
        logger.addHandler(fileHandler)
        return logger

    def _get_default_auth_request(self, controller: AuthController, *, timestamp=None, individual_id='', txn_id='', consent_obtained = False):
        _timestamp = timestamp or datetime.utcnow()
        timestamp_str = _timestamp.strftime(self.timestamp_format) + _timestamp.strftime('.%f')[0:4] + 'Z'
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
            ## BaseRequestDto(https://github.com/mosip/id-authentication/blob/d879209bc9e7c5aa7a84151372c450749fca5edf/authentication/authentication-core/src/main/java/io/mosip/authentication/core/indauth/dto/BaseRequestDTO.java#L13)
            id = id,
            version = self.ida_auth_version,
            individualId = individual_id,
            individualIdType = 'VID',
            transactionID = transaction_id,
            requestTime = timestamp_str,
            ## BaseAuthRequestDto
            specVersion = self.ida_auth_version,
            thumbprint = self.crypto_util.enc_cert_thumbprint,
            domainUri = self.auth_domain_scheme,
            env = self.ida_auth_env,
            ## AuthRequestDto
            request = '',
            consentObtained = consent_obtained,
            requestHMAC = '',
            requestSessionKey = '',
            metadata = {},
        )

    def kyc(self, *,
            vid,
            demographic_data: DemographicsModel,
            otp_value: Optional[str]='',
            biometrics: Optional[List[BiometricModel]]=[],
            consent_obtained = False,
            ):
        return self.__authenticate(
            controller='kyc',
            vid=vid,
            demographic_data=demographic_data,
            otp_value=otp_value,
            biometrics=biometrics,
            consent_obtained=consent_obtained,
        )

    def auth(self, *,
            vid,
            demographic_data: DemographicsModel,
            otp_value: Optional[str]='',
             biometrics: Optional[List[BiometricModel]]=[],
            consent_obtained = False,
            ):
        return self.__authenticate(
            controller='auth',
            vid=vid,
            demographic_data=demographic_data,
            otp_value=otp_value,
            biometrics=biometrics,
            consent_obtained=consent_obtained,
        )

    def __authenticate(
            self,
            *,
            controller: AuthController,
            vid: str,
            demographic_data: DemographicsModel,
            otp_value: Optional[str]='',
            biometrics: Optional[List[BiometricModel]]=[],
            consent_obtained=False,
    ):
        '''
        '''
        self.logger.info('Received Auth Request for demographic.')
        auth_request = self._get_default_auth_request(
            controller,
            individual_id=vid,
            consent_obtained=consent_obtained,
        )
        # auth_request.requestedAuth.demo = True
        # auth_request.requestedAuth.otp = bool(otp_value)
        # auth_request.requestedAuth.bio = bool(biometrics)
        request = MOSIPEncryptAuthRequest(
            timestamp = auth_request.requestTime,
            biometrics = biometrics or [],
            demographics = demographic_data,
            otp = otp_value,
        )
        try:
            auth_request.request, auth_request.requestSessionKey, auth_request.requestHMAC = \
                self.crypto_util.encrypt_auth_data(request.json(exclude_unset=True))
            path_params = '/'.join(
                map(
                    urllib.parse.quote,
                    (controller, self.partner_misp_lk, self.partner_id, self.partner_apikey)
                )
            )
            full_request_json = auth_request.json()
            self.logger.debug(f"{full_request_json=}")
            signature_header = {'Signature': self.crypto_util.sign_auth_request_data(full_request_json)}
            response = self.auth_rest_util.post_request(path_params=path_params, data=full_request_json, additional_headers=signature_header)
            self.logger.info('Auth Request for Demographic Completed.')
            return response
        except:
            exp = traceback.format_exc()
            self.logger.error('Error Processing Auth Request. Error Message: {}'.format(exp))
            raise AuthenticatorException(Errors.AUT_BAS_001.name, Errors.AUT_BAS_001.value)
