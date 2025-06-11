from pydantic import BaseModel

class AdElementDTOV2:
    class AdElementRequest(BaseModel):
        user_prompt: str


    class AdElementResponse(BaseModel):
        desc: str
        what: str
        how: str
        style: str