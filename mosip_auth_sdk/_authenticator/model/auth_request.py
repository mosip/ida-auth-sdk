from pydantic import BaseModel
from typing import List, Optional, Literal, Dict

class MOSIPRequestedAuth(BaseModel):
    demo : bool = False
    pin : bool = False
    otp : bool = False
    bio : bool = False

class IdentityInfo(BaseModel):
    language: str
    value: str

class DemographicsModel(BaseModel):
    age: str = None
    dob: str = ''
    name: List[IdentityInfo] = []
    dob_type: List[IdentityInfo] = []
    gender: List[IdentityInfo] = []
    phone_number: str = ''
    email_id: str = ''
    address_line1: List[IdentityInfo] = []
    address_line2: List[IdentityInfo] = []
    address_line3: List[IdentityInfo] = []
    location1: List[IdentityInfo] = []
    location2: List[IdentityInfo] = []
    location3: List[IdentityInfo] = []
    postal_code: str = ''
    full_address: List[IdentityInfo] = []
    metadata: Optional[Dict[str, object]] = None

class MOSIPEncryptAuthRequest(BaseModel):
    biometrics : list
    demographics : DemographicsModel
    otp : str
    timestamp : str


class MOSIPAuthRequest(BaseModel):
    id : str
    version : str
    individualId: str
    individualIdType: str
    transactionID: str
    requestTime: str
    specVersion: str
    thumbprint: str
    domainUri: str
    env: str
    requestedAuth : MOSIPRequestedAuth = MOSIPRequestedAuth()
    consentObtained: bool
    requestHMAC: str
    requestSessionKey: str
    request: str
    metadata: dict

class BiometricModelDataDigitalIdField(BaseModel):
    serialNo: str
    make: str
    model: str
    type: str
    deviceSubType: str
    deviceProvider: str
    dp: str
    dpId: str
    deviceProviderId: str
    dateTime: str

class BiometricModelDataField(BaseModel):
    digitalId: BiometricModelDataDigitalIdField
    bioType: str
    bioSubType: str
    bioValue: str
    deviceCode: str
    deviceServiceVersion: str
    transactionId: str
    timestamp: str
    purpose: str
    env: str
    version: str
    domainUri: str
    requestedScore: int
    qualityScore: int

class BiometricModel(BaseModel):
    data: BiometricModelDataField
    hash: str
    sessionKey: str
    specVersion: str
    thumbprint: str
