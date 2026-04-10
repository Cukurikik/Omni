# Unit test: AnalyticsEngine
from compute.analytics import AnalyticsEngine

def test_summary():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    s = AnalyticsEngine.summary(data)
    assert s['mean'] == 3.0
    assert s['count'] == 5