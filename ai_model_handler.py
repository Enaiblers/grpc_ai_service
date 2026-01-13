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
        self.output_names: list[str] = []
        self.input_name: str = ""

    def load_model(self, model_path: Path) -> bool:
        model_path = str(model_path.resolve())
        execution_providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]

        self._model = ort.InferenceSession(
            model_path, None, providers=execution_providers
        )
        if self._model is None :
            print("Could not load model")
            return False 
        try:
            self._model_author = self._model.get_modelmeta().custom_metadata_map[
                "author"
            ]
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 3
            opts.inter_op_num_threads = 3
            opts.enable_cpu_mem_arena = False
        except KeyError:
            self._model_author = "default"
            log.info("Could not find model author in metadata, setting default author")

        log.info(
            f"Loaded model from {model_path=}, with {self._model.get_providers()=}"
        )

        self.output_names = [x.name for x in self._model.get_outputs()]
        self.input_name = self._model.get_inputs()[0].name

        return True

    def run(self, output_names, input_feed, run_options=None):
        return self._model.run(output_names, input_feed, run_options)