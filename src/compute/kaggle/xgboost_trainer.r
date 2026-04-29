library(xgboost)

train_kaggle_xgboost <- function(train_data, train_label, test_data) {
  dtrain <- xgb.DMatrix(data = as.matrix(train_data), label = train_label)
  dtest <- xgb.DMatrix(data = as.matrix(test_data))
  
  params <- list(
    objective = "reg:squarederror",
    eta = 0.05,
    max_depth = 6,
    subsample = 0.8,
    colsample_bytree = 0.8
  )
  
  model <- xgb.train(params = params, data = dtrain, nrounds = 500)
  preds <- predict(model, dtest)
  return(preds)
}
