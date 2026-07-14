import argparse
import importlib
import sys


class CronRunner:
    JOB_MODULE_MAP = {
        "booking": "app.cron.booking.BookingCron",
        # Add new jobs here when created, for example:
        # "flights": "app.cron.flights.FlightsCron",
        # "cars": "app.cron.cars.CarsCron",
    }

    def __init__(self):
        self.args = self._parse_args()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="Run a cron job by name")
        parser.add_argument(
            "--job",
            required=True,
            choices=list(self.JOB_MODULE_MAP.keys()),
            help="Name of the cron job to run",
        )
        parser.add_argument("--from", dest="updated_from", default=None, help="updated_from date (YYYY-MM-DD)")
        parser.add_argument("--to", dest="updated_to", default=None, help="updated_to date (YYYY-MM-DD)")
        return parser.parse_args()

    def _load_class(self, dotted_path: str):
        module_path, class_name = dotted_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    def run(self):
        dotted_path = self.JOB_MODULE_MAP.get(self.args.job)
        if not dotted_path:
            print(f"Unknown job: {self.args.job}")
            sys.exit(1)

        job_class = self._load_class(dotted_path)
        job_instance = job_class(self.args.updated_from, self.args.updated_to)
        job_instance.run()


if __name__ == "__main__":
    CronRunner().run()