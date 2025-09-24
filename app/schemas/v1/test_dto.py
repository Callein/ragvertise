# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel


class GenerateTestReqDTO(BaseModel):
    system_prompt: str
    user_prompt: str
