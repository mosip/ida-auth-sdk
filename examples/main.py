from mosip_auth_sdk import MOSIPAuthenticator
from mosip_auth_sdk.models import DemographicsModel, BiometricModel
from dynaconf import Dynaconf

config = Dynaconf(
    settings_files=['./tests/authenticator-config.toml'],
    environments=False,
)

authenticator = MOSIPAuthenticator(config=config)
demographics_data = DemographicsModel(
    name=[{'language': 'en', 'value': 'Bathish'}],
    gender=[{'language': 'en', 'value': 'Male'}],
    dob="2002-12-01",
    phone_number="9876543210",
    email_id="arbathish@noreply.github.com",
    full_address=[{'language': 'en', 'value': '123 Main St'}]
)
response = authenticator.kyc(
    vid='4370296312658178',
    demographic_data=demographics_data,
)
resp_body = response.json()
errors = resp_body.get('errors') or []
if errors:
    for error in errors:
        print(error.get('errorCode'), ':', error.get('errorMessage'))

print(response.status_code)
