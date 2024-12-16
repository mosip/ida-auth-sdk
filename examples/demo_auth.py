from mosip_auth_sdk import MOSIPAuthenticator
from mosip_auth_sdk.models import DemographicsModel
from dynaconf import Dynaconf
import sys

config = Dynaconf(
    settings_files=["./config.toml"],
    environments=False,
)
authenticator = MOSIPAuthenticator(config=config)
demographics_data = DemographicsModel(
    dob="1992/01/01"
)
print("Demographics data:", demographics_data.model_dump())


response = authenticator.auth(
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

print(response_body)
