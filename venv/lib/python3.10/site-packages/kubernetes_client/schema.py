
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, validator


__all__ = [
    "ResourceSpec",
]


MEMField = Field(
    2, title="Memory size",
    ge=0.1, le=128, multiple_of=0.1,
)

CPUField = Field(
    1, title="CPU size",
    ge=0.1, le=64, multiple_of=0.1,
)

GPUField = Field(
    0, title="GPU count",
    ge=0, le=8, multiple_of=1,
    alias="nvidia.com/gpu",
)

REPLICAField = Field(
    1, title="replica",
    ge=0, le=10_000, multiple_of=1,
)

CONCURRENCYField = Field(
    100, title="concurrency",
    ge=1, le=10_000, multiple_of=1,
)

NAMEField = Field(
    "", title="k8s namespace",
    max_length=200,
)


class Spec(BaseModel):
    cpu: Optional[int] = CPUField
    memory: Optional[float] = MEMField
    gpu: Optional[int] = GPUField

    @validator("memory", always=True)
    def format_memory(cls, v):
        return f"{v}Gi"


class ResourceSpec(BaseModel):
    requests: Optional[Spec] = None
    limits: Optional[Spec] = None

    def _validate_minmax(
            cls,
            request: Union[int, float],
            limit: Union[int, float]
            ) -> Union[int, float]:
        if limit < request:
            return request
        else:
            return limit

    @validator("limits", always=True)
    def validate_minmax(cls, v, values, **kwargs):
        requests = values['requests']
        if v is not None and requests is not None:
            requests_dict = values['requests'].dict()
            return Spec(**{
                cls._validate_minmax(
                    request=requests_dict[type],
                    limit=value,
                )
                if type in requests_dict else value
                for type, value in v.dict().items()
            })


