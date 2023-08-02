from pydantic import BaseModel


class RespModel(BaseModel):
    error: str | None


class ErrorResp(RespModel):
    error: str


class SuccessResp(RespModel):
    error: None = None


class PostLogin(BaseModel):
    email: str
    passwd: str


class PostLoginResp(SuccessResp):
    refresh_token: str


class EntityResp(SuccessResp):
    result: list[dict]


class PostRefreshResp(SuccessResp):
    access_token: str


class MailSend(BaseModel):
    content: str


class PostTaskResp(SuccessResp):
    result_id: str
