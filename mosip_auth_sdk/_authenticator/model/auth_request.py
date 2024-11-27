from pydantic import BaseModel
from typing import List, Optional, Literal

class MOSIPRequestedAuth(BaseModel):
    demo : bool = False
    pin : bool = False
    otp : bool = False
    bio : bool = False

class DemographicLanguageField(BaseModel):
    language: str
    value: str

class DemographicsModel(BaseModel):
    name : List[DemographicLanguageField]
    gender : List[DemographicLanguageField]
    dob : str
    phoneNumber : Optional[str]
    emailId : Optional[str]
    fullAddress : List[DemographicLanguageField]

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
