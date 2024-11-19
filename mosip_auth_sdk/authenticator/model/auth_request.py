from pydantic import BaseModel
from typing import List, Optional

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
    timestamp : str
    demographics : dict
    biometrics : list

class MOSIPAuthRequest(BaseModel):
    id : str
    version : str
    individualId: str
    #individualIdType: str = 'VID'
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

class BiometricModelDigitalId(BaseModel):
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

class BiometricModelData(BaseModel):
    digitalId: DigitalId
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
    data: BiometricModelData
    hash: str
    sessionKey: str
    specVersion: str
    thumbprint: str
