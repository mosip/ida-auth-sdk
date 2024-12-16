from mosip_auth_sdk import MOSIPAuthenticator
from mosip_auth_sdk.models import DemographicsModel
from dynaconf import Dynaconf
import sys

config = Dynaconf(
    settings_files=["./authenticator-config.toml"],
    environments=False,
)
authenticator = MOSIPAuthenticator(config=config)
demographics_data = DemographicsModel(
    name=[{"language": "eng", "value": "jevan  mksm"}],
)
print("Demographics data:", demographics_data.model_dump())


response = authenticator.kyc(
    individual_id="4370296312658178",
    individual_id_type="VID",
    demographic_data=demographics_data,
    consent=True,
)
response_body = response.json()
errors = response_body.get("errors") or []
if errors:
    for error in errors:
        print(error.get("errorCode"), ":", error.get("errorMessage"))
    sys.exit(1)

print(response.status_code)
decrypted_response = authenticator.decrypt_response(response_body)
print(decrypted_response)
