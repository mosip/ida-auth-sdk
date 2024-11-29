# Mosip Authentication SDK

# Usage
```python
    from mosip_auth_sdk import MOSIPAuthenticator
    from mosip_auth_sdk.models import DemographicsModel, BiometricModel
    
    # Initialize the authenticator with configuration settings
    authenticator = MOSIPAuthenticator(config={
        # Your configuration settings go here.
        # Refer to authenticator-config.toml for the required values.
    })
    
    # Prepare demographic data
    demographics_data = DemographicsModel(
        # Provide demographic details based on your needs
    )
    
    # Make a KYC request
    response = authenticator.kyc(
        individual_id='<some_id>',  # Replace with actual ID
        individual_id_type='VID',  # Replace with the type of ID being used
        demographic_data=demographics_data,
        otp_value='<otp_value>',  # Optional
        biometrics=biometrics,  # Optional
        consent=True  # Indicates if consent has been obtained
    )
    
    # Handle the response
    response_body = response.json()
    errors = response_body.get('errors', [])
    
    if errors:
        # Handle errors
        pass
    else:
        # Process the successful response
        decrypted_response = authenticator.decrypt_response(response_body)
        # Further processing with decrypted_response
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
