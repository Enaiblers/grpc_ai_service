from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NDArray(_message.Message):
    __slots__ = ("data", "shape", "dtype")
    DATA_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    shape: _containers.RepeatedScalarFieldContainer[int]
    dtype: str
    def __init__(
        self,
        data: _Optional[bytes] = ...,
        shape: _Optional[_Iterable[int]] = ...,
        dtype: _Optional[str] = ...,
    ) -> None: ...

class NDArrayList(_message.Message):
    __slots__ = ("arr",)
    ARR_FIELD_NUMBER: _ClassVar[int]
    arr: _containers.RepeatedCompositeFieldContainer[NDArray]
    def __init__(
        self, arr: _Optional[_Iterable[_Union[NDArray, _Mapping]]] = ...
    ) -> None: ...

class RunRequest(_message.Message):
    __slots__ = ("model_uuid", "input", "run_options")
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    RUN_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    input: NDArray
    run_options: bytes
    def __init__(
        self,
        model_uuid: _Optional[str] = ...,
        input: _Optional[_Union[NDArray, _Mapping]] = ...,
        run_options: _Optional[bytes] = ...,
    ) -> None: ...

class RunResponse(_message.Message):
    __slots__ = ("output", "output_names")
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_NAMES_FIELD_NUMBER: _ClassVar[int]
    output: NDArrayList
    output_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(
        self,
        output: _Optional[_Union[NDArrayList, _Mapping]] = ...,
        output_names: _Optional[_Iterable[str]] = ...,
    ) -> None: ...

class ModelInfoRequest(_message.Message):
    __slots__ = ("model_uuid",)
    MODEL_UUID_FIELD_NUMBER: _ClassVar[int]
    model_uuid: str
    def __init__(self, model_uuid: _Optional[str] = ...) -> None: ...

class ModelInfoResponse(_message.Message):
    __slots__ = (
        "modelAuthor",
        "output_names",
        "input_names",
        "input_height",
        "input_width",
        "input_channels",
    )
    MODELAUTHOR_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_NAMES_FIELD_NUMBER: _ClassVar[int]
    INPUT_NAMES_FIELD_NUMBER: _ClassVar[int]
    INPUT_HEIGHT_FIELD_NUMBER: _ClassVar[int]
    INPUT_WIDTH_FIELD_NUMBER: _ClassVar[int]
    INPUT_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    modelAuthor: str
    output_names: _containers.RepeatedScalarFieldContainer[str]
    input_names: str
    input_height: int
    input_width: int
    input_channels: int
    def __init__(
        self,
        modelAuthor: _Optional[str] = ...,
        output_names: _Optional[_Iterable[str]] = ...,
        input_names: _Optional[str] = ...,
        input_height: _Optional[int] = ...,
        input_width: _Optional[int] = ...,
        input_channels: _Optional[int] = ...,
    ) -> None: ...

class LoadModelRequest(_message.Message):
    __slots__ = ("modelPath",)
    MODELPATH_FIELD_NUMBER: _ClassVar[int]
    modelPath: str
    def __init__(self, modelPath: _Optional[str] = ...) -> None: ...

class LoadModelResponse(_message.Message):
    __slots__ = ("loadStatus",)
    LOADSTATUS_FIELD_NUMBER: _ClassVar[int]
    loadStatus: bool
    def __init__(self, loadStatus: bool = ...) -> None: ...
