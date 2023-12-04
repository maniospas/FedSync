import random

from fedsync.data import FedKeras
import multiprocessing
import demo


class SimulatedServer(multiprocessing.Process):
    def __init__(self, **kwargs):
        super(SimulatedServer, self).__init__()
        self.kwargs = kwargs

    def run(self):
        from waitress import serve
        x, y = demo.train_data(random.randint(10, 50)*random.randint(10, 50))
        model = FedKeras(demo.model(), lambda model, repetition: demo.train(model, repetition, x, y))
        app = model.app()
        print(f"Simulated server started: {str(self.kwargs)} with {int(x.shape[0])} samples")
        serve(app, **self.kwargs)


if __name__ == "__main__":
    num_processes = 2
    processes = []
    for i in range(num_processes):
        process = SimulatedServer(host="127.0.0.1", port=8000+i)
        processes.append(process)
        process.start()
    for process in processes:
        process.join()
