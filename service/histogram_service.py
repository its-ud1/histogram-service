from service.histogram import Histogram
from typing import List
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv() #loading the enviorment

class HistogramService: #service --> for seperating the business logic from the controller and the class 
    def __init__(self):
        self.histogram = Histogram() #injecting the histogram instance in the service layer 
        self.load_intervals_from_file()

    def load_intervals_from_file(self): # getting the file absolute location using the .env file and starts parsing
        file_rel_path = os.getenv("INTERVAL_FILE_PATH", "intervals.txt") # not working from .env config
        file_path = Path(__file__).parent.parent.parent / file_rel_path
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        interval = self.parse_interval(line)
                        if interval:
                            self.histogram.add_interval(interval)
                self.histogram.post_parse_operations()
        except FileNotFoundError:
            raise FileNotFoundError(f"Interval file not found on location : {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error loading intervals: {e}")

    def parse_interval(self, line: str): #reading each line and validating
        try:
            start, end = line.strip("[]()").split(',')
            start = float(start)
            end = float(end)
            if start >= end:
                print(f"Invalid interval: [{start}, {end})") 
                return None
            return (start, end)
        except ValueError:
            print(f"Failed to parse interval please check the file format again: {line}")
            return None

    def insert_samples(self, samples: List[float]):
        self.histogram.insert_samples(samples)
    
    def get_metrics(self):
        return self.histogram.get_metrics()