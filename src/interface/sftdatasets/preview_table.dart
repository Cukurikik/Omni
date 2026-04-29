class OmniResult<T> {
  final T? value;
  final String? error;
  final bool isOk;

  OmniResult({this.value, this.error}) : isOk = error == null;
}

class PreviewTable {
  OmniResult<bool> renderTable(List<Map<String, String>> datasetRows) {
    if (datasetRows.isEmpty) {
      return OmniResult(error: 'Dataset is empty');
    }

    // Dart frontend logic for SFT dataset preview rendering
    print('Rendering ${datasetRows.length} rows for data inspection...');
    
    return OmniResult(value: true);
  }
}
