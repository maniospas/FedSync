import requests
import json
from time import sleep


class Remote:
    def __init__(self, address):
        self.address = address

    def _result(self, repetition="last"):
        response = requests.get(f"{self.address}/{repetition}/result")
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                raise Exception(f"{self.address}: {data['error']}")
            return data["success"]
        else:
            raise Exception("GET Request Failed")

    def result(self, repetition="last"):
        ret = None
        while ret is None:
            ret = self._result(repetition)
            sleep(0.2)
        return ret

    def submit(self, specs, params, repetition="new"):
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({
            "specs": specs,
            "params": params
        })
        response = requests.post(f"{self.address}/{repetition}/submit", headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                raise Exception(f"{self.address}: {data['error']}")
            return data["success"]
        else:
            raise Exception("GET Request Failed")


class Federated:
    def __init__(self, data, remotes):
        self.data = data
        self.remotes = remotes
        self.repetition = 0

    def round(self):
        self.repetition += 1
        specs = self.data.specs(self.repetition)
        params = self.data.serialize(self.repetition)
        [remote.submit(specs, params, repetition=self.repetition) for remote in self.remotes]
        encodings = [remote.result(repetition=self.repetition) for remote in self.remotes]
        self.data.merge(encodings, self.repetition)
