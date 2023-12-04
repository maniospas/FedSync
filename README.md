# FedSync

Synchronized federated algorithms across remote devices.

:warning: These algorithms requre constant communication.

**Author:** Emmanouil (Manios) Krasanakis<br>
**License:** Apache 2.0

## Fedavg on Keras models
You need to run several servers and clients. Each 
server hosts a fragment of one dataset and an approximation
of a machine learning model. It should also have a method
that tries to further train this model over a fixed number 
of epochs while returning the model's weight.

```python
from fedsync.data import FedKeras

x, y = ... # local training data
def train(model):
    model.fit(x, y, epochs=...)
    return x.shape[0]
    
model = ... # create a keras model
model = FedKeras(model, train)
```


The exact same model declaration should be present 
across all servers and
be made known to the client. The latter
declares the remote servers and constructs a federated
averaging algorithm like so:

```python
model = ...  # the created keras model
alg = Federated(
    data=FedKeras(model, None),
    remotes=[
        Remote("http://127.0.0.1:8000"),
        Remote("http://127.0.0.1:8001"),
    ],
)
for round in range(...):
    alg.round() # a full federated averaging round to obtain an improved model
    # show some validation here (and can include a convergence check)
```


## Custom data

You can create your own data exchange schemas
by inheriting from the base `FedData` class and
implementing the following methods:
- `specs` a short specification string that can be checked for compliance between datatypes (this can be sha256 of machine learning model configurations)
- `serialize` a data serialization method,
- `receive` actions to perform when a server receives data 
- `merge` actions to perform when a client merges data from several servers.

```python
from fedsync.data import FedData, FIRST

class FedFloat(FedData):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def specs(self, repetition):
        return "Float"

    def receive(self, encoding, repetition):
        if repetition == FIRST:
            return
        self.value = float(encoding)

    def merge(self, encodings, repetition):
        encodings = [float(encoding) for encoding in encodings]
        self.value = sum(encodings)/len(encodings)

    def serialize(self, repetition):
        return str(self.value)
```