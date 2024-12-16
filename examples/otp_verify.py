from mosip_auth_sdk import MOSIPAuthenticator
from dynaconf import Dynaconf

import sys

config = Dynaconf(
    settings_files=["./config.toml"],
    environments=False,
)
authenticator = MOSIPAuthenticator(config=config)

response = authenticator.kyc(
    individual_id="4370296312658178",
    individual_id_type="VID",
    otp_value="111111",
    consent=True,
    txn_id="8300715076"
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