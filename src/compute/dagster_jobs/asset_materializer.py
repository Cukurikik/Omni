from omni.core import Result, Ok, Err

class AssetMaterializer:
    def materialize(self, asset_key: str) -> Result[bool, Exception]:
        if not asset_key:
            return Err(Exception("Missing asset key"))
        return Ok(True)
