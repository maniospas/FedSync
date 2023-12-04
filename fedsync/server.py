from flask import Flask, request, jsonify
from time import sleep
import threading


FIRST = 1


class Task:
    def __init__(self, received, repetition):
        self.received = received
        self.completed = None
        self.repetition = repetition


class FedData:
    def __init__(self):
        self._tasks = dict()
        self._repetition = 0
        self._lock = threading.Lock()
        self._pending = list()
        self.runner = threading.Thread(target=self._runner)

    def _runner(self):
        while True:  # run tasks in fifo order, which is synchronized with this loop
            # get task to work on (currently only one task in queue allowed, but this may change)
            self._lock.acquire()
            if not self._pending:
                sleep(0.2)
                self._lock.release()
                continue
            task = self._pending[0]
            self._lock.release()

            # work on the task and get data to send
            self.receive(task.received, repetition=task.repetition)
            task.completed = self.serialize(repetition=task.repetition)

            # remove task from queue
            self._lock.acquire()
            self._pending.pop(0)
            self._lock.release()

    def app(self):
        app = Flask("FedTF")

        @app.route('/<repetition>/result', methods=['GET'])
        def get_data(repetition):
            self._lock.acquire()
            try:
                repetition = self._repetition - 1 if repetition == "last" else int(repetition)
                ret = self._tasks[repetition].completed
                self._lock.release()
                return jsonify({'success': ret})
            except Exception as e:
                return jsonify({'error': e.__class__.__name__+": "+str(e)})

        @app.route('/<repetition>/submit', methods=['POST'])
        def set_data(repetition):
            self._lock.acquire()
            try:
                repetition = self._repetition + 1 if repetition == "new" else int(repetition)
                if repetition != self._repetition+1:
                    self._lock.release()
                    return jsonify({'error': "Can only submit data to a new repetition."})
                if self._pending:
                    self._lock.release()
                    return jsonify({'error': "Can not submit while a task is already running."})
                data = request.json
                local_specs = self.specs(repetition)
                if local_specs != data["specs"]:
                    self._lock.release()
                    return jsonify({'error': "Incompatible specification: please contact the server owner."})
                task = Task(data["params"], repetition)
                #self._tasks[repetition] = task
                self._tasks = {repetition: task}  # keep track of only the last task
                self._pending.append(task)
                self._repetition = max(self._repetition, repetition)
                self._lock.release()
                return jsonify({'success': "Parameters submitted successfully."})
            except Exception as e:
                self._lock.release()
                return jsonify({'error': str(e)})
        self.runner.start()
        return app
