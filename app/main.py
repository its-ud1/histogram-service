from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from service.histogram_service import HistogramService
from app.model import SampleRequest

app = FastAPI()
histogram_service = HistogramService() #injecting the service instance in the controller layer

@app.post("/insertSamples")
async def insert_samples(request: SampleRequest):
    if not request.samples:
        raise HTTPException(status_code=400, detail="No samples provided")
    for sample in request.samples:
        if not isinstance(sample, float):
            raise HTTPException(status_code=400, detail=f"Invalid sample value: {sample}")
    histogram_service.insert_samples(request.samples)
    return JSONResponse(
        status_code=200,
        content={"message": "Samples inserted successfully"}
    )

@app.get("/metrics")
async def get_metrics():
    metrics = histogram_service.get_metrics()
    return JSONResponse(
        status_code=200,  # or use status.HTTP_200_OK
        content={"metrics": metrics}
    )
