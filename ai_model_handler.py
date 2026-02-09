# Copyright (C) 2026 Enaiblers AB
# SPDX-License-Identifier: AGPL-3.0-or-later
import logging
from pathlib import Path

import onnxruntime as ort

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


class AIModelHandler:
    def __init__(self, model_uuid: str) -> None:
        self._model_uuid = model_uuid
        self._model = None
        self._output_names: list[str] = []
        self._input_name: str = ""
        self._model_author: str = ""

    def load_model(self, model_path: Path) -> bool:
        model_path = str(model_path.resolve())
        execution_providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        self._model = ort.InferenceSession(
            model_path, None, providers=execution_providers
        )
        if self._model is None:
            log.info("Could not load model")
            return False
        try:
            self._model_author = self._model.get_modelmeta().custom_metadata_map[
                "author"
            ]
        except KeyError:
            self._model_author = "default"
            log.debug("Could not find model author in metadata, setting default author")

        log.debug(
            f"Loaded model from {model_path=}, with {self._model.get_providers()=}"
        )

        self._output_names = [x.name for x in self._model.get_outputs()]
        self._input_name = self._model.get_inputs()[0].name

        return True

    def run(self, output_names, input_feed, run_options=None):
        return self._model.run(output_names, input_feed, run_options)

    @property
    def model_uuid(self) -> str:
        return self._model_uuid

    @property
    def model(self):
        return self._model

    @property
    def output_names(self) -> list[str]:
        return self._output_names

    @property
    def input_name(self) -> str:
        return self._input_name

    @property
    def model_author(self) -> str:
        return self._model_author
