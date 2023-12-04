from fedsync.server import FedData, FIRST
import hashlib
import pickle
import numpy as np
import base64


class FedFloat(FedData):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def specs(self, repetition):
        return "Float"

    def receive(self, encoding, repetition):
        if repetition == FIRST:
            return
        value = float(encoding)
        self.value = (value+self.value)*0.5

    def merge(self, encodings, repetition):
        encodings = [float(encoding) for encoding in encodings]
        self.value = sum(encodings)/len(encodings)

    def serialize(self, repetition):
        return str(self.value)


class FedKeras(FedData):
    def __init__(self, model, fit):
        super().__init__()
        self.model = model
        self.fit = fit
        # for faster communication encode the configuration with sha256 - this makes it very
        # unlikely that different specifications are determined at the client and the servers
        # (this is not a security measure - just a debugging check for well-meaning clients)
        self.config_hash = hashlib.sha256(str(self.model.to_json()).encode("utf-8")).hexdigest()
        self.num_samples = None  # dynamically set this by each fit to send alongside with the weights


    def specs(self, repetition):
        return self.config_hash

    def _deserialize(self, encoding):
        return pickle.loads(base64.b64decode(encoding["weights"].encode())), encoding["samples"]

    def receive(self, encoding, repetition):
        assert encoding["samples"] is None
        self.model.set_weights(self._deserialize(encoding)[0])
        self.num_samples = self.fit(self.model, repetition)

    def merge(self, encodings, repetition):
        weight_lists = [self._deserialize(enc) for enc in encodings]
        weights = []
        total_samples = float(sum([samples for _, samples in weight_lists]))
        for i in range(len(weight_lists[0][0])):
            weight = 0
            for list, samples in weight_lists:
                weight = list[i]*(samples/total_samples)+weight
            weights.append(weight)
        self.model.set_weights(weights)

    def serialize(self, repetition):
        return {
            "weights": base64.b64encode(pickle.dumps(self.model.get_weights())).decode(),
            "samples": self.num_samples
        }


