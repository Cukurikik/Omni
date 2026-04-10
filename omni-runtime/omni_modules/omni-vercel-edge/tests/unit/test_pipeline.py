# Unit test: DataPipeline execute
import pytest
from compute.pipeline import DataPipeline

def test_pipeline_execute():
    p = DataPipeline()
    p.add_stage('double', lambda x: x * 2)
    p.add_stage('add10', lambda x: x + 10)
    result = p.execute(5)
    assert result.success
    assert result.data == 20

def test_pipeline_error():
    p = DataPipeline()
    p.add_stage('fail', lambda x: 1/0)
    result = p.execute(5)
    assert not result.success