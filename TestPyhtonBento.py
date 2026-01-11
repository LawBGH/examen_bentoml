python3 - << 'EOF'
import bentoml
print(bentoml.sklearn.load_model("linear_regression_model:latest"))
print(bentoml.sklearn.load_model("data_scaler:latest"))
EOF
