import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
from pathlib import Path
from .electrode_formulation import ElectrodeFormulation

def create_chemistry_combination():
    """
    Create a dictionary of chemistries with their respective electrode formulations.
    """
    chemistry_combinations = {}
    positive_electrode_formulations = [ElectrodeFormulation(chem) for chem in ['NMC811', 'LFP', 'NCA', 'LCO']]
    negative_electrode_formulations = [ElectrodeFormulation(chem) for chem in ['Graphite', 'Si5%+Graphite95%', 'Si10%+Graphite90%', 'Si20%+Graphite80%', 'Si40%+Graphite60%']]
    
    # Create combinations of positive and negative electrode formulations
    for pos in positive_electrode_formulations:
        for neg in negative_electrode_formulations:
            # Create a unique key for each combination
            key = f"{pos.material_properties['Name']}/{neg.material_properties['Name']}"
            nominal_voltage = pos.material_properties['Electrode nominal voltage [V]']-neg.material_properties['Electrode nominal voltage [V]']
            gravimetric_energy_density = 0.55*(pos.material_properties['Electrode specific capacity [mAh.g-1]']*nominal_voltage/(1+ pos.material_properties['Electrode specific capacity [mAh.g-1]']/neg.material_properties['Electrode specific capacity [mAh.g-1]']))
            chemistry_combinations[key] = {
                "Positive electrode formulation": pos,
                "Negative electrode formulation": neg,
                "Cell nominal voltage [V]": np.random.uniform(nominal_voltage*0.999, nominal_voltage*1.001),  # Example nominal voltage range
                "Gravimetric energy density [Wh/kg]": np.random.uniform(gravimetric_energy_density*0.999, gravimetric_energy_density*1.001)  # Example gravimetric energy density range
            }
            print(f"Created chemistry combination: {key} with nominal voltage {chemistry_combinations[key]['Cell nominal voltage [V]']} V and gravimetric energy density {chemistry_combinations[key]['Gravimetric energy density [Wh/kg]']} Wh/kg")
    return chemistry_combinations


# Non mcp functions
def train_chemistry_model():
    # Create directory if it doesn't exist
    cwd = Path(__file__).parent

    # Generate synthetic dataset
    np.random.seed(42)  # For reproducibility
    n_samples_per_chemistry = 100
    data = []
    labels = []
    models = {}
    # Generate data for each chemistry
    # Each chemistry will have a range of nominal voltages, and gravimetric energy densities
    # The ranges are based on typical values for these chemistries
    # The ranges are defined as [min_nominal_voltage, max_nominal_voltage, min_gravimetric, max_gravimetric]
    # The data will be generated uniformly within these ranges

    chemistries = create_chemistry_combination()
    for i, chem in enumerate(chemistries):
        for _ in range(n_samples_per_chemistry):
            nominal_voltage = chemistries[chem]["Cell nominal voltage [V]"]
            gravimetric_density = chemistries[chem]["Gravimetric energy density [Wh/kg]"]
            data.append([nominal_voltage, gravimetric_density])
            labels.append(chem)

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Cell nominal voltage [V]", "Gravimetric energy density [Wh/kg]"])
    df["Chemistry"] = labels

    # Prepare features and target
    X = df[["Cell nominal voltage [V]", "Gravimetric energy density [Wh/kg]"]]
    y = df["Chemistry"]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
    
    # Get unique positive electrode materials
    unique_positives = set()
    for chem in y_train:
        pos = chem.split('/')[0]
        unique_positives.add(pos)
    unique_positives = sorted(unique_positives)
    for pos in unique_positives:
        mask = y_train.str.contains(pos)
        X_chem = X_train.loc[mask]
        y_chem = y_train[mask]
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_chem[["Gravimetric energy density [Wh/kg]"]], y_chem)
        models[pos] = model
    
    # Save the trained model
    model_path = cwd / "battery_chemistry_model.joblib"
    joblib.dump(models, model_path)
    print(f"Trained model saved as '{model_path}'")

if __name__ == "__main__":
    # Uncomment the line below to train the model
    train_chemistry_model()
    pass
