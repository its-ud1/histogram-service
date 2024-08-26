from typing import List, Tuple
from fastapi import HTTPException
import threading

class Histogram:
    def __init__(self):
        self.__intervals = [] # stores the unoverlapped and valid intervals getting by reading the intervals.txt file
        self.__counts = {} # dictionary storing the frequesncy of elements occoured in the perticular interval range key = interval, value = frequency
        self.__total_samples = 0 # total number of samples falls under the given list of intervals 
        self.__sum_samples = 0.0 # cumulative sum of the samples falling in the interval range 
        self.__sum_squares = 0.0 # squared sum of the samples falling in the interval range
        self.__outliers = [] # list of samples falling outside the interval range
        self.__mean = 0.0 # mean of all the samples falling under interval range
        self.__variance = 0.0 #variance of all the samples falling under interval range
        self.__is_operlapping_intervals = False #flag denoting weather the intervals are overlapping or not
        self.__is_invalid_interval = False # flag denoting weather the interval coming from the intervals.tx file in valid or not
        self.lock = threading.Lock()  # for thread safety

    def get_total_samples(self): #for accessing the private variable
        return self.__total_samples 
    
    def add_interval(self, interval: tuple[float, float]): #adding the tuple of interval in the intervals list
        self.__intervals.append(interval)
        self.__counts[interval] = 0

    def __binary_search_in_intervals(self, sample: float) -> int:
        low, high = 0, len(self.__intervals) - 1
        while low <= high:
            mid = low + (high -low) // 2
            if self.__intervals[mid][0] <= sample < self.__intervals[mid][1]:
                return mid
            elif sample < self.__intervals[mid][0]:
                high = mid - 1
            else:
                low = mid + 1
        return -1
    
    def __insert_sample(self, sample: float):
        index = self.__binary_search_in_intervals(sample) #not sure weather to include or exclude it in self.lock() ??
        with self.lock: ## ensuring thread safety while encountering simultaneous access of this function 
            if index != -1:
                interval = self.__intervals[index]
                self.__counts[interval] += 1
                self.__total_samples += 1
                self.__sum_samples += sample
                self.__sum_squares += sample ** 2
            else:
                self.__outliers.append(sample)

    def insert_samples(self, samples: List[float]):
        if(self.__is_invalid_interval):
            raise HTTPException(status_code = 500, detail = "Invalid intervals found, please correct the intervals in intervals.txt file.")
        if(self.__is_operlapping_intervals):
            raise HTTPException(status_code = 500, detail = "Overlapping intervals found, please correct the intervals in intervals.txt file.")
        for sample in samples:
            self.__insert_sample(sample)

        #post insert operations for calculating the mean and variance for the new samples collected till now
        if self.__total_samples != 0:
            self.__mean = self.__sum_samples / self.__total_samples
            self.__variance = (self.__sum_squares / self.__total_samples) - (self.__mean ** 2)
        self.__outliers.sort()

    def get_metrics(self):
        if(self.__is_invalid_interval):
            raise HTTPException(status_code = 500, detail = "Invalid intervals found, please correct the intervals in intervals.txt file.")
        if(self.__is_operlapping_intervals):
            raise HTTPException(status_code = 500, detail = "Overlapping intervals found, please correct the intervals in intervals.txt file.")
        interval_stats = {str(interval).replace('(','['): count for interval, count in self.__counts.items()}
        metrics = {
            "interval_counts": interval_stats,
            "sample_mean": round(self.__mean, 3),
            "sample_variance": round(self.__variance, 3),
            "outliers": self.__outliers
        }
        return metrics
    
    def __has_operlapping_intervals(self) -> bool:
        # intervals are already sorted in post parse operation so it saves one step
        for i in range(1, len(self.__intervals)):
            if self.__intervals[i][0] < self.__intervals[i-1][1]:
                return True
        return False

    def __has_invalid_interval(self) -> bool:
        for interval in self.__intervals:
            start, end = interval
            if(start >= end):
                return True
        return False

    def post_parse_operations(self): #after reading the whole file we are sorting the collected lists and dictionaries which will help in optimized search operations and generating cleaner response 
        self.__intervals.sort()  # Keeping intervals sorted
        self.__is_operlapping_intervals = self.__has_operlapping_intervals()
        self.__is_invalid_interval = self.__has_invalid_interval()
        self.__counts = {key: self.__counts[key] for key in sorted(self.__counts)} #keeping the dictionary sorted wrt keys i.e. intervals 