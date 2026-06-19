import anndata
import argparse
import numpy as np
import os
import pandas as pd
import scanpy as sc
import scvi
from scvi.model import TOTALVI
import sys
import torch
import warnings

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


# sets path for ref_model and ref_adata
def get_model_path(ref_model, ref_adata):
    """Fetch the model and reference data paths directly from user input."""
    if not os.path.exists(ref_model):
        raise FileNotFoundError(f"Reference model file not found: {ref_model}")

    if not os.path.exists(ref_adata):
        raise FileNotFoundError(f"Reference AnnData file not found: {ref_adata}")

    return ref_model, ref_adata


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process AnnData for TOTALVI")
    input_data = parser.add_argument_group('Input Data')
    input_data.add_argument('--adata_file', type=str, required=False, help="Path to the input AnnData file")
    input_data.add_argument('--RNApath', type=str, help="Path to RNA counts file (CSV format)")
    input_data.add_argument('--metapath', type=str, help="Path to metadata file (CSV format)")
    input_data.add_argument('--ADTpath', type=str, help="Path to ADT counts file (CSV format)")
    input_data.add_argument('--umappath', type=str, required=False, help="Path to UMAP file (CSV format)")

    parser.add_argument('--ref_model', type=str, required=True, help="Path to the reference model file")
    parser.add_argument('--ref_adata', type=str, required=True, help="Path to the reference AnnData file")
    parser.add_argument('--classifier_type', type=str, choices=["BBC", "BRF"], default="BBC", help="Classifier type to use for NK cell classification (BBC or BRF)")

    parser.add_argument('--output_dir', type=str, default="./output", help="Directory to save output files")
    parser.add_argument('--protein', action='store_true', help="Flag to include protein data")
    parser.add_argument('--batch', type=str, default="sample", help="Batch column to use in AnnData")
    parser.add_argument('--proteins_file', type=str, required=True, 
                        help="Path to a file containing proteins to exclude from protein_expression.")
    parser.add_argument('--protein_suffix', type=str, default='-TotalSeqC', 
                        help="Suffix to be replaced from protein names in the expression matrix.")
    parser.add_argument('--adversarial_classifier', type=str, choices=["None", "True", "False"], default="None",
                        help="Enable adversarial classifier in TOTALVI (None, True, False)")
    parser.add_argument('--mouse', action='store_true', help="Flag to process mouse genes (mm10)")
    parser.add_argument('--patient', type=str, required=True, help="Name of the patient or dataset being processed")
    parser.add_argument('--disable_NK_type', action='store_true', help="Disable NK cell classification v1.1 step")
    # In parse_arguments
    parser.add_argument('--proteintech', action='store_true',
                    help="Flag if ADT data is in ProteinTech format e.g. 'prot:CD16.65090.1' → 'CD16ADT'.")
    return parser.parse_args()


def validate_files(adata_file, RNApath, metapath, umappath, ADTpath, protein):
    """Check if input files exist."""
    files = [adata_file, RNApath, metapath]

    if umappath:  # Only validate UMAP path if it's provided
        files.append(umappath)

    if protein:  # Only validate ADTpath if protein is True
        files.append(ADTpath)
    for file in files:
        if file and not os.path.exists(file):
            raise FileNotFoundError(f"File not found: {file}")

def load_proteins_from_file(file_path):
    """Load protein names from a file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Protein file not found: {file_path}")

    # Read the file; assume it's a plain text file with one protein per line
    with open(file_path, 'r') as f:
        proteins = [line.strip() for line in f.readlines()]
    
    return proteins

def validate_data_integrity(RNA_counts, ADT_counts):
    if RNA_counts.shape[0] != ADT_counts.shape[0]:
        raise ValueError(f"Mismatch in number of cells: RNA ({RNA_counts.shape[0]}) vs ADT ({ADT_counts.shape[0]}).")
    
    if not RNA_counts.obs_names.equals(ADT_counts.obs_names):
        raise ValueError("Mismatch in barcodes between RNA and ADT counts.")
    
    if any(RNA_counts.obs_names != ADT_counts.obs_names):
        raise ValueError("Barcode names do not match between RNA and ADT counts.")
    
    print("RNA and ADT data integrity validated successfully.")

def load_data(adata_file, ref_adata, RNApath, metapath, umappath, ADTpath, protein):
    """Load AnnData objects and external data."""
    if adata_file:
        adata = sc.read_h5ad(adata_file)
    else:
        adata = sc.read_csv(RNApath)
        adata = adata.transpose()
        meta = pd.read_csv(metapath, index_col=0)
        adata.obs = meta
        # Convert all object columns to string type
        for col in adata.obs.select_dtypes(include=['object']).columns:
            adata.obs[col] = adata.obs[col].astype(str)
        if umappath:     # Only process UMAP if a path is given
            umap = pd.read_csv(umappath, index_col=0)
            adata = adata[umap.index]
            umap = umap.to_numpy()  # Convert to array
            adata.obsm["X_umap"] = umap

    # Load the reference data
    ref = sc.read_h5ad(ref_adata)

    # Check if protein data already exists in adata
    if protein and "protein_expression" in adata.obsm:
        protein_adata = adata.obsm["protein_expression"].copy()
        del adata.obsm["protein_expression"]  # force reprocessing

    elif protein and ADTpath:
        # If protein flag is set and ADTpath is provided, load the ADT data
        protein_adata = sc.read_csv(ADTpath)
        protein_adata = protein_adata.transpose()

        # Validate integrity between RNA and ADT data
        validate_data_integrity(adata, protein_adata)

        # inspect the indexes:
        print('Protein Indexes Before')
        print(protein_adata.obs.index)
        
        protein_adata.obs.index = protein_adata.obs.index.str.replace('X', '') # note default value of regex changing in other versions, current default is True
        protein_adata.obs.index = protein_adata.obs.index.str.replace('\.', '-', regex = True)
        print('Protein Indexes After')
        print(protein_adata.obs.index)
        print()

    else:
        protein_adata = None

    return adata, ref, protein_adata


def preprocess_data(adata, protein, protein_adata, ref, meta, batch, proteins_to_check,
                    protein_suffix, proteintech, output_dir, patient, mouse):
    if protein:
        if protein_adata is not None:
            adata = integrate_protein_data(adata, protein_adata, meta, proteins_to_check,
                                           protein_suffix, proteintech)
    else:
        adata = initialize_protein_data(adata, ref)
    
    adata = prepare_adata_for_totalvi(adata, batch, ref, output_dir, patient, mouse)
    return adata

# Updated integrate_protein_data to include proteintech data
def integrate_protein_data(adata, protein_adata, meta, proteins_to_check, protein_suffix, proteintech):
    """Integrate protein expression data into the AnnData object.
    
    Supports two protein naming formats:
    - Standard (default): CD16-TotalSeqC → CD16ADT (use --protein_suffix)
    - ProteinTech: prot:CD16.65090.1 → CD16ADT (use --proteintech flag)
    """
        
    if "protein_expression" not in adata.obsm:
        if isinstance(protein_adata, pd.DataFrame):
            adata.obsm["protein_expression"] = protein_adata
        else:
            protein_adata.obs = meta
            adata.obsm["protein_expression"] = protein_adata.to_df()
    
    cols = adata.obsm["protein_expression"].columns

    if proteintech:
        # Handle ProteinTech format: prot:CD16.65090.1 → CD16ADT
        cols = cols.str.replace('prot:', '', regex=False).str.split('.').str[0] + 'ADT'
        print("ProteinTech format detected. Renamed protein columns to ADT format.")
    else:
        # Handle standard format: CD16-TotalSeqC → CD16ADT
        cols = cols.str.replace(protein_suffix, 'ADT', regex=True)

    adata.obsm["protein_expression"].columns = cols
    print(f"Protein names after renaming: {cols.tolist()}")

    adata.obsm["protein_expression"] = adata.obsm["protein_expression"][
        adata.obsm["protein_expression"].columns.difference(proteins_to_check)]
    
    return adata


def initialize_protein_data(adata, ref):
    """Initialize protein expression data with zeros."""
    pro_exp = ref.obsm["protein_expression"]
    data = np.zeros((adata.n_obs, pro_exp.shape[1]))
    adata.obsm["protein_expression"] = pd.DataFrame(columns=pro_exp.columns, index=adata.obs_names, data=data)

    return adata


def prepare_adata_for_totalvi(adata, batch, ref, output_dir, patient, mouse):
    """Prepare AnnData for TOTALVI."""
    adata.obs['batch'] = adata.obs[batch]

    if mouse:
        print("Filtering out mouse genes (mm10)...")
        adata.var['mouse'] = adata.var_names.str.startswith('mm10')
        adata = adata[:, ~adata.var['mouse']]
        del adata.var['mouse']  # Remove to avoid conflicts in TOTALVI

    #adata.raw = adata

    adata.layers["counts"] = adata.X.copy()

    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    adata.raw = adata
    adata.obs["celltype.l2"] = "Unknown"

    align_protein_data(adata, ref, output_dir, patient)
    ref.obs["dataset_name"] = "Reference"
    adata.obs["dataset_name"] = "Query"
    prepped_file = os.path.join(output_dir, f'{patient}_prepped.h5ad')
    adata.write(prepped_file)
    return adata

def align_protein_data(adata, ref, output_dir, patient):
    """Align protein expression data to the reference."""
    print(adata.obsm.keys())

    adata.obsm["protein_expression"] = adata.obsm["protein_expression"].reindex(
        columns=ref.obsm["protein_expression"].columns, fill_value=0.0)
    
    return adata

def train_totalvi_model(adata, ref_model, ref, adversarial_classifier):
    """Train the TOTALVI model on the query data."""
    print("Loading pre-trained TOTALVI model...")
    vae = TOTALVI.load(ref_model, ref)
    print("Preparing query AnnData for TOTALVI...")
    try:
        TOTALVI.prepare_query_anndata(adata, reference_model=vae)
        print(f"Keys in adata.obsm after prepare_query_anndata: {adata.obsm.keys()}")
    except Exception as e:
        raise ValueError(f"Failed to prepare query AnnData: {e}")

    print("Training TOTALVI query model...")
    vae_q = TOTALVI.load_query_data(adata, vae)
    
    # Convert string input to Python types
    # Convert string input to Python types
    if adversarial_classifier == "None":
        adv_classifier = None
    elif adversarial_classifier == "True":
        adv_classifier = True
    elif adversarial_classifier == "False":
        adv_classifier = False
    else:
        raise ValueError(f"Invalid value for adversarial_classifier: {adversarial_classifier}")

    vae_q.train(
        max_epochs=150,
        plan_kwargs=dict(weight_decay=0.0, scale_adversarial_loss=0.0),
        adversarial_classifier=adv_classifier
    )

    print(f"Training status: {vae_q.is_trained}")

    # Check latent space generation
    try:
        latent_rep = vae_q.get_latent_representation(adata)
        print(f"Shape of latent representation: {latent_rep.shape}")
        adata.obsm["X_totalvi_scarches"] = latent_rep
    except Exception as e:
        raise ValueError(f"Failed to generate latent space: {e}")

    print("Model training complete. Latent space created successfully.")
    return vae_q


def classify_latent_space(vae_q, adata, classifier_type):
    """Classify using BBC or BRF based on the selected model."""
    if classifier_type == "BBC":
        predictions = vae_q.latent_space_classifer_bbc_.predict(adata.obsm["X_totalvi_scarches"])
        probs = vae_q.latent_space_classifer_bbc_.predict_proba(adata.obsm["X_totalvi_scarches"])
    elif classifier_type == "BRF":
        predictions = vae_q.latent_space_classifer_brf_.predict(adata.obsm["X_totalvi_scarches"])
        probs = vae_q.latent_space_classifer_brf_.predict_proba(adata.obsm["X_totalvi_scarches"])
    else:
        raise ValueError(f"Unknown classifier type '{classifier_type}'")

    predictions = np.where(predictions == "ML1", "eML1", predictions)
    predictions = np.where(predictions == "ML2", "eML2", predictions)

    print("Classifier predictions completed")
    return predictions, probs



def save_results(adata, predictions, probs, output_dir, patient, vae_q, classifier_type, mouse):
    """Save all relevant results based on the classifier used."""
    df_probs = pd.DataFrame(probs, columns=getattr(vae_q, f"latent_space_classifer_{classifier_type.lower()}_").classes_, index=adata.obs_names)

    # Save probabilities to CSV
    df_probs.to_csv(os.path.join(output_dir, f'{patient}_probabilities{classifier_type}output.csv'))

    dfi_probs = df_probs.loc[adata.obs_names]

    # Add probability columns to adata.obs dynamically
    adata.obs[f"CD56bright{classifier_type}prob"] = dfi_probs["CD56bright"]
    adata.obs[f"CD56dim{classifier_type}prob"] = dfi_probs["CD56dim"]
    adata.obs[f"eML1{classifier_type}prob"] = dfi_probs["ML1"]
    adata.obs[f"eML2{classifier_type}prob"] = dfi_probs["ML2"]

    # Add predictions to adata.obs
    adata.obs[f"predictions{classifier_type}"] = predictions
    print(adata.obs.columns)  # This will show all the columns in `adata.obs`
    print(f"Classifier type: {classifier_type}")

    # **Ensure `adata.var['mouse']` is deleted before saving, if mouse processing was enabled**
    if mouse and 'mouse' in adata.var:
        del adata.var['mouse']

    # Save the classified AnnData object
    classified_file = os.path.join(output_dir, f'{patient}_eMLclassified_adata.h5ad')
    adata.write_h5ad(classified_file)
    print("Saved the classified AnnData object")

    # Save the updated VAE model
    vae_model_file = os.path.join(output_dir, f'{patient}_vae_model_withclassifiers')
    vae_q.save(vae_model_file, overwrite=True)

    print("Saved the updated VAE model")


def classify_cells(adata, classifier_type, output_dir, patient):
    """
    Classifies cells based on {classifier_type} probabilities stored in adata.obs.
    Assigns 'ML_transition', 'unclassified', or the label with the highest probability.
    
    """
    probability_columns = [f'CD56bright{classifier_type}prob', f'CD56dim{classifier_type}prob', f'eML1{classifier_type}prob', f'eML2{classifier_type}prob']
    labels = ['CD56bright', 'CD56dim', 'eML1', 'eML2']
    
    # Ensure probability columns are numeric
    for col in probability_columns:
        adata.obs[col] = pd.to_numeric(adata.obs[col], errors='coerce')
    
    # Classification function
    def classify_row(row):
        if all(row[col] < 0.5 for col in probability_columns):
            if row[f'eML1{classifier_type}prob'] + row[f'eML2{classifier_type}prob'] > 0.5:
                return 'eML_transition'
            else:
                return 'unclassified'
        else:
            max_index = row[probability_columns].astype(float).idxmax()
            return labels[probability_columns.index(max_index)]
    
    # Apply nk type classification function
    adata.obs['NK_type'] = adata.obs.apply(classify_row, axis=1)
    
    # Save the classified AnnData object
    classified_file = os.path.join(output_dir, f'{patient}_eMLclassified_adata.h5ad')
    adata.write_h5ad(classified_file)
    
    return adata

def main():
    """Main function to execute the process."""

    args = parse_arguments()

    # Create the output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Save arguments to a file for later review
    args_file = os.path.join(args.output_dir, f'{args.patient}_arguments_used.txt')
    with open(args_file, 'w') as f:
        for key, value in vars(args).items():
            f.write(f"{key}: {value}\n")
    print(f"Arguments saved to {args_file}")

    # Load proteins from the specified file
    proteins_to_check = load_proteins_from_file(args.proteins_file)
    
    # Validate file paths
    validate_files(args.adata_file, args.RNApath, args.metapath, args.umappath, args.ADTpath, args.protein)

    # Get model paths
    ref_model, ref_adata = get_model_path(args.ref_model, args.ref_adata)

    # Load data
    adata, ref, protein_adata = load_data(args.adata_file, ref_adata, args.RNApath, args.metapath, args.umappath, args.ADTpath, args.protein)
    meta = adata.obs.copy()

    # Preprocess data
    adata = preprocess_data(adata, args.protein, protein_adata, ref, adata.obs, args.batch, proteins_to_check, args.protein_suffix, args.proteintech, args.output_dir, args.patient, args.mouse)
    # Train the model
    vae_q = train_totalvi_model(adata, ref_model, ref, args.adversarial_classifier)

    # Classify the data
    predictions, probs = classify_latent_space(vae_q, adata, args.classifier_type)

    # Save results
    save_results(adata, predictions, probs, args.output_dir, args.patient, vae_q, args.classifier_type, args.mouse)

    # Run classification by default unless disabled
    if not args.disable_NK_type:
        adata = classify_cells(adata, args.classifier_type, args.output_dir, args.patient)
        print(adata.obs["NK_type"].value_counts())
    else:
        print("NK Cell classification v1.1 step skipped.")

    print("All output files are saved in output directory")

if __name__ == "__main__":
    main()
    