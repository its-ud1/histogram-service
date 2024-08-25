import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient
from app.main import app  # Import your FastAPI app

# Mocking the HistogramService
@pytest.fixture
def mock_histogram_service(monkeypatch):
    mock_service = MagicMock()
    mock_service.insert_samples = AsyncMock()
    mock_service.get_metrics = AsyncMock(return_value={
        "interval_counts": {}, 
        "sample_mean": 0.0, 
        "sample_variance": 0.0, 
        "outliers": []
    })
    monkeypatch.setattr("app.main.histogram_service", mock_service)
    return mock_service

@pytest.mark.asyncio
async def test_insert_samples(mock_histogram_service):
    async with AsyncClient(app= app, base_url="http://test") as ac:
        # Test valid sample insertion
        valid_payload = {"samples": [1.5, 2.3, 3.7]}
        response = await ac.post("/insertSamples", json=valid_payload)
        assert response.status_code == 200
        assert response.json() == {
            "message": "Samples inserted successfully"
        }
        mock_histogram_service.insert_samples.assert_called_once_with([1.5, 2.3, 3.7])

        # Test no samples provided
        empty_payload = {"samples": []}
        response = await ac.post("/insertSamples", json=empty_payload)
        assert response.status_code == 400
        assert response.json() == {"detail": "No samples provided"}
        mock_histogram_service.insert_samples.assert_called_once()  # No new call should be made

        # Test invalid sample type
        invalid_payload = {"samples": [1.5, "invalid_sample"]}
        response = await ac.post("/insertSamples", json=invalid_payload)
        assert response.status_code == 422
        mock_histogram_service.insert_samples.assert_called_once()  # No new call should be made

# @pytest.mark.asyncio
# async def test_get_metrics(mock_histogram_service):
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/metrics")
#         assert response.status_code == 200
#         assert response.json() == {
#             "status": "success",
#             "metrics": {
#                 "interval_counts": {},
#                 "sample_mean": 0.0,
#                 "sample_variance": 0.0,
#                 "outliers": []
#             }
#         }
#         # Correctly await the async mock call
#         await mock_histogram_service.get_metrics.assert_called_once()
