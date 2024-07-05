import sys
import util

class FleetManager:

    def __init__(self):
        self.vehicles = []
        self.jobs = {}
        self.hq = util.Point(0, 0)
        self.time_limit = 12 * 60

    def load_jobs(self, filepath):
        job_list = util.loadProblemFromFile(filepath)
        for task in job_list:
            self.jobs[int(task.id)] = task

    def compute_savings(self):
        savings_list = []
        for task1_id in self.jobs:
            for task2_id in self.jobs:
                if task1_id != task2_id:
                    task1 = self.jobs[task1_id]
                    task2 = self.jobs[task2_id]
                    pair = (task1_id, task2_id)
                    saving_value = (pair,
                                    util.distanceBetweenPoints(task1.dropoff, self.hq)
                                    + util.distanceBetweenPoints(self.hq, task2.pickup)
                                    - util.distanceBetweenPoints(task1.dropoff, task2.pickup))
                    savings_list.append(saving_value)

        savings_list.sort(key=lambda x: x[1], reverse=True)
        return savings_list

    def get_route_distance(self, job_sequence):
        if not job_sequence:
            return 0.0

        total_dist = 0.0
        for i in range(len(job_sequence)):
            total_dist += job_sequence[i].delivery_distance
            if i != (len(job_sequence) - 1):
                total_dist += util.distanceBetweenPoints(job_sequence[i].dropoff, job_sequence[i + 1].pickup)

        total_dist += util.distanceBetweenPoints(self.hq, job_sequence[0].pickup)
        total_dist += util.distanceBetweenPoints(job_sequence[-1].dropoff, self.hq)
        return total_dist

    def show_solution(self):
        for vehicle in self.vehicles:
            print([int(task.id) for task in vehicle.route])

    def find_routes(self):

        savings_list = self.compute_savings()

        for (task1_id, task2_id), _ in savings_list:
            task1 = self.jobs[task1_id]
            task2 = self.jobs[task2_id]

            if not task1.assigned and not task2.assigned:
                cost = self.get_route_distance([task1, task2])
                if cost <= self.time_limit:
                    vehicle = util.Driver()
                    vehicle.route = [task1, task2]
                    self.vehicles.append(vehicle)
                    task1.assigned = vehicle
                    task2.assigned = vehicle

            elif task1.assigned and not task2.assigned:
                vehicle = task1.assigned
                if vehicle.route.index(task1) == len(vehicle.route) - 1:
                    cost = self.get_route_distance(vehicle.route + [task2])
                    if cost <= self.time_limit:
                        vehicle.route.append(task2)
                        task2.assigned = vehicle

            elif not task1.assigned and task2.assigned:
                vehicle = task2.assigned
                if vehicle.route.index(task2) == 0:
                    cost = self.get_route_distance([task1] + vehicle.route)
                    if cost <= self.time_limit:
                        vehicle.route = [task1] + vehicle.route
                        task1.assigned = vehicle

            else:
                vehicle1 = task1.assigned
                vehicle2 = task2.assigned
                if vehicle1 != vehicle2 and vehicle1.route.index(task1) == len(vehicle1.route) - 1 and vehicle2.route.index(task2) == 0:
                    cost = self.get_route_distance(vehicle1.route + vehicle2.route)
                    if cost <= self.time_limit:
                        vehicle1.route.extend(vehicle2.route)
                        for task in vehicle2.route:
                            task.assigned = vehicle1
                        self.vehicles.remove(vehicle2)

        for task in self.jobs.values():
            if not task.assigned:
                vehicle = util.Driver()
                vehicle.route.append(task)
                self.vehicles.append(vehicle)
                task.assigned = vehicle


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fleet_manager.py <file_path>")
        sys.exit(1)
    filepath = sys.argv[1]
    manager = FleetManager()
    manager.load_jobs(filepath)
    manager.find_routes()
    manager.show_solution()

