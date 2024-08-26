# Histogram Web Service

## Overview

This project implements an asynchronous web service that manages a histogram. The service reads intervals from an input file, allows for sample insertion, and provides metrics on the current state of the histogram.

### Key Features

- Mean and Variance are calculated in constant time ( O(1) ).
- Used Binary-Search for frequency calclation in the sorted interval list bought down the complexity from O(n) --> O(log n)
- Precalculated the Invalid intervals and Overlapped intervals to reduce the redundant computation on each API call
- Used fixtures to mock the service calls to reject and return the response artifically depending on the scenario
- Unittest covering the possible scenarios of samples adding 
- **Thread-Safe Histogram**: Manages intervals and samples in a thread-safe manner to avoid race conditions.
- **Asynchronous Endpoints**: Provides asynchronous API endpoints for inserting samples and retrieving metrics.
- **Resilient to Errors**: Handles erroneous input data by discarding invalid intervals or samples.
- **Real-Time Metrics**: Calculates and returns the sample mean, variance, and outliers.
## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- pytest (for running tests)

### Setup

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/yourusername/histogram-web-service.git
    cd histogram-web-service
    ```

2. **Create a Virtual Environment** (optional but recommended):
    ```bash
    python -m venv venv
    Set-ExecutionPolicy Unrestricted -Scope Process # (optional) needed in my case (windows) to enable virtual env creation on your local machine
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Service

1. **Start the Web Service**:
    ```bash
    uvicorn app.main:app --host localhost --port 8000 --reload
    ```

2. **Access the API**:

   - **Insert Samples**: `POST /insertSamples`
     - Endpoint to insert an array of floating point numbers.
   - **Get Metrics**: `GET /metrics`
     - Endpoint to retrieve the current statistics of the histogram.

### Configuration

- **Input File**: The service reads intervals from a file located in `assets/intervals.txt`.

### API Endpoints

- **POST /insertSamples**
  - Inserts an array of floating point numbers into the histogram.
  - Example request body:
    ```json
    {
        "samples": [3.5, 4.2, 8.0, 31.5]
    }
    ```

- **GET /metrics**
  - Retrieves the current histogram statistics.
  - Example response:
    ```json
    {
        "metrics": {
                "interval_counts": {
                "[0, 1.1)": 1,
                "[3, 4.1)": 0,
                "[8.5, 8.7)": 0,
                "[31.5, 41.27)": 2
            },
            "sample_mean": 24.203,
            "sample_variance": 422.243,
            "outliers": [4.2, 8.1, 8.2, 30, 41.27]
        }
    }
    ```

### Testing env setup
- (make sure) all the requirements written in requirments.txt should be installed
- Take a new terminal in venv
- move to the tests folder from histogram_service by command (cd /tests)
- for running tests for histogram.py give terminal command: pytest .\test_histogram.py (for windows)
- for running tests for main.py give terminal command: pytest .\test_main.py (for windows)

### Test Results

- **Test for `histogram.py`**:

    ![histogram.py](https://github.com/its-ud1/histogram-service/blob/master/images/ss2.png)

- **Test for `main.py`**:

    ![main.py](https://github.com/its-ud1/histogram-service/blob/master/images/ss1.png)


- ### List of installed packages (pip list for venv)
annotated-types   0.7.0
anyio             4.4.0
asyncio           3.4.3
attrs             24.2.0
Automat           24.8.1
certifi           2024.7.4
click             8.1.7
colorama          0.4.6
constantly        23.10.4
decorator         5.1.1
exceptiongroup    1.2.2
fastapi           0.112.2
greenlet          3.0.3
h11               0.14.0
httpcore          1.0.5
httpx             0.27.0
hyperlink         21.0.0
idna              3.8
incremental       24.7.2
iniconfig         2.0.0
numpy             2.1.0
packaging         24.1
pip               24.2
pluggy            1.5.0
pydantic          2.8.2
pydantic_core     2.20.1
pytest            8.3.2
pytest-asyncio    0.24.0
pytest-twisted    1.14.2
python-dotenv     1.0.1
setuptools        73.0.1
sniffio           1.3.1
starlette         0.38.2
tomli             2.0.1
Twisted           24.7.0
typing_extensions 4.12.2
uvicorn           0.30.6
zope.interface    7.0.1