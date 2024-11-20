# Mosip Authentication SDK

# Usage
```python
    from mosip_auth_sdk import MOSIPAuthenticator
    from mosip_auth_sdk.models import DemographicsModel, BiometricModel

    authenticator = MOSIPAuthenticator(config={
        # Your configuration settings go here.
        # Refer to authenticator-config.toml for the required values.
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
    
    # handle response
```

# Prerequisites for building
* Python 3 (tested on 3.10.7), lower versions may or may not work.
* Poetry (recommended, optional)
  install
  ```sh
  python3 -m pip install poetry
  ```
  
# Dependencies for building
  ```sh
    python3 -m poetry install
  ```
  If you don't want to use poetry you can install the requirements directly using pip
  ```sh
  python3 -m pip install -r requirements.txt
  ```
# Build
    ```sh
    python3 -m poetry build
    ```

# Publish
```sh
    python3 -m poetry publish
```

# Testing
