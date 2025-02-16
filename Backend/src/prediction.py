def predict_accessibility_score(model, example):
    return model.run(**example)