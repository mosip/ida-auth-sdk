# Mosip Authentication SDK

MOSIP Authentication SDK is a Python wrapper for interacting with the MOSIP Authentication Service, enabling developers to integrate authentication workflows into their systems. The SDK simplifies the interaction with MOSIP's backend authentication services, providing methods to authenticate individuals based on demographic data, biometrics, and other identifiers.

## Controllers

MOSIP provides two main authentication controllers:

1. **kyc-auth-controller**  
   Used for Know Your Customer (KYC) authentication, which includes verifying identity using demographic data and biometrics.  
   [API Documentation](https://mosip.github.io/documentation/1.2.0/authentication-service.html#tag/kyc-auth-controller)

2. **auth-controller**  
   Used for general authentication of individuals, allowing for verification based on a variety of identifiers and biometric data.  
   [API Documentation](https://mosip.github.io/documentation/1.2.0/authentication-service.html#operation/authenticateIndividual)

## Methods

### `kyc` Method

```python
kyc(individual_id: str, individual_id_type: str, demographic_data: DemographicsModel, otp_value: str = None, biometrics: list[BiometricModel] = None, consent: bool = False) -> Response
```

### `auth` Method

```python
auth(individual_id: str, individual_id_type: str, demographic_data: DemographicsModel, otp_value: Optional[str] = None, biometrics: Optional[List[BiometricModel]] = None, consent: bool = False) -> Response
```

### Common Parameters

- **individual_id (str)**: The unique ID of the individual to authenticate (e.g., VID, UIN)
- **individual_id_type (str)**: The type of the ID being used (e.g., VID, UIN)
- **demographic_data (DemographicsModel)**: The demographic data for the individual (e.g., name, address)
- **otp_value (Optional[str])**: The One-Time Password (OTP) value, if applicable (default is None)
- **consent (bool)**: Indicates whether consent has been obtained for authentication (default is False)

## Installation

```bash
pip install mosip_auth_sdk
```

## Usage

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

## Development Setup

### Prerequisites
- Python 3 (tested on 3.10.7)
- Poetry (recommended, optional)

### Install Poetry
```bash
python3 -m pip install poetry
```

### Install Dependencies
Using Poetry:
```bash
python3 -m poetry install
```

Using pip:
```bash
python3 -m pip install -r requirements.txt
```

### Build
```bash
python3 -m poetry build
```

### Publish
```bash
python3 -m poetry publish
```

## Testing

Example code is available in the `examples` folder. To test:

```bash
python examples/main.py
```
