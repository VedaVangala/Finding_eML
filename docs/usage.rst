Usage
=====

This section describes how to use Finding eML package. 

Types of Files that Can Be Used
--------------------------------

You can use the tool with either an **AnnData (.h5ad)** file or a combination of **CSV files**.

AnnData File (`.h5ad`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--adata_file`` argument to pass a file in `.h5ad` format. The AnnData object must contain:

- ``.X``: RNA expression matrix (cells × genes)
- ``.obs``: metadata
- ``.obsm``: optional UMAP or protein data

CSV Files
~~~~~~~~~~~~~~~~~

If ``--adata_file`` is not provided, you must supply the following CSV files:

- ``--RNApath``: Gene × Cell matrix (rows = genes, columns = cell barcodes)
- ``--metapath``: Metadata (rows = cell barcodes)
- ``--ADTpath`` (optional): Cell × ADT matrix (rows = cell barcodes, columns = proteins)
- ``--umappath`` (optional): UMAP coordinates (rows = cell barcodes + 2D coordinates)



Command-Line Arguments
-----------------------
.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Argument
     - Required
     - Description

   * - ``--adata_file``
     - If absent CSV required
     - Path to AnnData, raw counts layer required in ``.X``.
   * - ``--RNApath``
     - If absent adata required
     - Path to the RNA counts file (CSV format).
   * - ``--metapath``
     - If absent adata required
     - Path to the metadata file (CSV format).
   * - ``--umappath``
     - Optional
     - Path to the UMAP file (CSV format).
   * - ``--ADTpath``
     - Optional
     - Path to the ADT counts file (CSV format).
   * - ``--ref_model``
     - Yes
     - Path to the reference model file
   * - ``--ref_adata``
     - Yes
     - Path to the reference AnnData file
   * - ``--batch``
     - Yes
     - Specifies the batch column in AnnData. Defaults to ``sample``.
   * - ``--proteins_file``
     - Yes
     - Path to the file with proteins to exclude from protein expression.
   * - ``--patient``
     - Yes
     - Specify it for file namining as prefix for output files.
   * - ``--output_dir`` 
     - Optional
     - The directory to save output files. Defaults to ``./output``.
   * - ``--classifier_type``
     - No
     - Defaults to classifier type, ``BBC``     
   * - ``--protein``
     - No
     - Flag to include protein data if specified.     
   * - ``--protein_suffix``
     - No
     - Suffix to replace in protein names in the expression matrix. Defaults to ``'-TotalSeqC'``.
   * - ``--adversarial_classifier``
     - No
     - Defaults to ``"None"``. For further information, check `Scvi-tools Documentation <https://docs.scvi-tools.org/en/stable/api/reference/scvi.model.TOTALVI.html>`_.
   * - ``--mouse``
     - No
     - Flag to remove mouse genes (mm10).
   * - ``--disable_NK_type``
     - No
     - Flag to disable additional v1.1 NK cell categories. Gives only v1.0 NK cell categories.
   * - ``--proteintech``
     - No
     - Flag if ADT data is in ProteinTech format e.g. 'prot:CD16.65090.1' → 'CD16ADT'.



Protein Data Inclusion
----------------------

To include protein (ADT) data in classification, choose one of the following:

**Scenario A: Using ADT File via ``--ADTpath``**

If proteins are stored in a CSV file:

- Provide ``--ADTpath`` (cell × ADT matrix)
- Use ``--protein`` flag
- Provide ``--proteins_file`` to exclude specific proteins

The ADT CSV must be formatted with cell barcodes as **rows** and protein names as **columns**.

**Scenario B: Proteins Already Present in AnnData (.obsm)**

If protein expression is already embedded in AnnData (e.g., in ``.obsm['protein_expression']``):

- Use ``--protein`` flag
- Provide ``--proteins_file`` to exclude specific proteins
- ``--ADTpath`` is not needed

The protein file contains list of proteins to be removed. protein_file is flexible to take other protein files too, if you want to customize the protein removal.

.. code-block:: bash

   IgG2aADT
   IgG2bADT
   IgG1ADT
   PD-1ADT
   CD8ADT
   KIR2DL1-S1-S3-S5ADT
   KIR2DL2-3ADT
   KIR3DL1ADT
   KIR2DL5ADT

Notes on Data Shapes
--------------------

- ``.h5ad`` (AnnData) format:
  - ``.X``: cells × genes
  - ``.obsm``: can contain UMAP (e.g., ``X_umap``) and protein matrix

- CSV format:
  - ``RNApath``: genes × cells
  - ``ADTpath``: cells × proteins
  - ``metapath``: one row per cell