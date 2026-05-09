(: OMNI Database Layer: XQuery :)
(: Script to query and extract dataset manifests from the XML-based Omni Data Lake :)

xquery version "3.1";

declare namespace omni = "http://omniframework.dev/schema/dataset";

(: Given an XML document containing thousands of dataset metadata entries, 
   we extract only those formatted for Transformer ingestion (e.g., text/multimodal)
   and possessing a quality score > 0.95 :)

let $catalog := doc("omni_dataset_catalog.xml")/omni:Catalog

return
  <OmniTrainingManifest>
  {
    for $dataset in $catalog/omni:Dataset
    where $dataset/@format = "tfrecords"
      and xs:float($dataset/omni:QualityScore) > 0.95
      and $dataset/omni:Modality = "multimodal"
    order by xs:date($dataset/omni:IngestionDate) descending
    return
      <TrainingJob>
        <DatasetID>{ data($dataset/@id) }</DatasetID>
        <S3URI>{ data($dataset/omni:Location) }</S3URI>
        <EstimatedTokens>{ data($dataset/omni:TokenCount) }</EstimatedTokens>
      </TrainingJob>
  }
  </OmniTrainingManifest>
