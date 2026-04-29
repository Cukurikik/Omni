/* Omni Interpretability View (ReasonML) */
/* Interface Layer: Type-safe functional rendering of Mechanistic Interpretability data. */

type tensorData = {
  layerIndex: int,
  activationSparsity: float,
};

let renderTensorView = (data: tensorData) => {
  let isSparse = data.activationSparsity > 0.8;
  let statusColor = isSparse ? "#2EA043" : "#D29922";
  
  /* Returns deterministic layout string (representing virtual DOM node) */
  "[OMNI_RENDER] <View layer=" ++ string_of_int(data.layerIndex) ++ 
  " color=" ++ statusColor ++ ">Sparsity: " ++ string_of_float(data.activationSparsity) ++ "</View>";
};

let exampleData = { layerIndex: 12, activationSparsity: 0.85 };
let _ = renderTensorView(exampleData);
