from fedsync.client import Federated, Remote
from fedsync.data import FedKeras
import demo

model = demo.model()
alg = Federated(
    data=FedKeras(model, None),
    remotes=[
        Remote("http://127.0.0.1:8000"),
        Remote("http://127.0.0.1:8001"),
    ],
)
for round in range(10):
    print(f"===== Communication round {round+1} ======")
    alg.round()
    demo.test(model)
