# Finding eML Documentation

![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.12-blue)
![scRNA-seq](https://img.shields.io/badge/analysis-scRNA--seq-purple)
![NK cells](https://img.shields.io/badge/cell%20type-NK%20cells-teal)
![pan-cancer](https://img.shields.io/badge/scope-pan--cancer-orange)
![Machine Learning](https://img.shields.io/badge/method-machine%20learning-yellow)
[![Documentation](https://readthedocs.org/projects/finding-eml/badge/?version=latest)](https://finding-eml.readthedocs.io/en/latest/)

Full documentation for the **Finding eML** package — a machine learning classifier for identifying and analyzing memory-like (ML) NK cells from single-cell RNA sequencing data.

📄 **[View Full Documentation](https://finding-eml.readthedocs.io/en/latest/)**

---

## 📑 Documentation Sections

1. 🗂️ Outline
2. ⚙️ Usage
3. 🚀 Running the Tool — Direct and Interactive Execution
4. 🔬 API — Source Code
   
---

## 🗂️ Outline

📄 **[Read full Outline →](https://finding-eml.readthedocs.io/en/latest/outline.html)**

The Outline section covers v1.0 and v1.1 categories and how they are obtained, along with details about the classifier, root structure, functions, and execution.

**v1.0** — classifies NK cells into 4 categories:
- CD56dim (NK1)
- CD56bright (NK2)
- eML1 / iML1
- eML2 / iML2

**v1.1** — classifies NK cells into 6 categories:
- CD56dim (NK1)
- CD56bright (NK2)
- eML1 / iML1
- eML2 / iML2
- eML_transition / iML_transition
- Unclassified

---

## ⚙️ Usage & Direct Execution

📄 **[Read full Usage →](https://finding-eml.readthedocs.io/en/latest/usage.html)**

### Supported Input Formats
- CSV (`.csv`) — RNA counts and metadata
- AnnData (`.h5ad`)

### Docker 🐳
Docker image required: `veda504/finding_eml:v1.1`

### Arguments

| Argument | Description |
|---|---|
| `--batch` | Custom batch column name based on experiment/dataset |
| `--adversarial_classifier` | Turn on (`True`/`None`) or off (`False`) |
| `--protein_file` | Already included in package, call as `/app/...` |
| `--ref_model` | Already included in package, call as `/app/...` |
| `--ref_adata` | Already included in package, call as `/app/...` |
| `--classifier_type` | Default: BBC (Balanced Bagging Classifier) |
| `--output_dir` | Path to output directory |
| `--patient` | Prefix added to output file names |
| `--disable_NK_type` | Flag to disable v1.1 categories, gives only v1.0 categories |

---

## 🚀 Running the Tool

📄 **[Read full Running the Tool →](https://finding-eml.readthedocs.io/en/latest/running_tool.html)**

After running Docker, the classifier script is called using:

```bash
python3 -m eML.classify <arguments>
```

### Direct Execution
📄 **[Read Direct Execution →](https://finding-eml.readthedocs.io/en/latest/direct.html)**

### Interactive Execution
📄 **[Read Interactive Execution →](https://finding-eml.readthedocs.io/en/latest/interactive.html)**

### 💡 Notes

- If protein data is present and needs to be added to the classifier run, `--protein` should be flagged and `--protein_suffix` is required to replace `-TotalSeqC` to get format of `CD16ADT`.
- Each step of execution can also be run separately using the **[interactive execution](https://finding-eml.readthedocs.io/en/latest/interactive.html)** method.
- Reference data and protein file are already included in the package. `--protein_file`, `--ref_model`, `--ref_adata` need to be called as shown in the example run (`/app/…`).

---

## 🔬 API — Source Code

📄 **[Read full API →](https://finding-eml.readthedocs.io/en/latest/modules.html)**

Full API reference and source code documentation:
- **[classify module →](https://finding-eml.readthedocs.io/en/latest/classify.html)**

---

## 📚 Citations

If you use Finding eML in your research, please cite:

**Finding eML:**
Foltz JA, Tran J, Wong P, et al. Cytokines drive the formation of memory-like NK cell subsets via epigenetic rewiring and transcriptional regulation. *Science Immunology.* 2024;9(96):eadk4893. https://doi.org/10.1126/sciimmunol.adk4893

**TotalVI:**
Gayoso A, Steier Z, Lopez R, et al. Joint probabilistic modeling of single-cell multi-omic data with totalVI. *Nat Methods.* 2021;18(3):272-282. https://doi.org/10.1038/s41592-020-01050-x

**scVI (scvi-tools):**
Gayoso A, Lopez R, Xing G, et al. A Python library for probabilistic analysis of single-cell omics data. *Nat Biotechnol.* 2022;40(2):163-166. https://doi.org/10.1038/s41587-021-01206-w

**SCANPY:**
Wolf FA, Angerer P, Theis FJ. SCANPY: large-scale single-cell gene expression data analysis. *Genome Biol.* 2018;19(1):15. https://doi.org/10.1186/s13059-017-1382-0

**Imbalanced-learn:**
Lemaitre G, Nogueira F, Aridas CK. Imbalanced-learn: A Python Toolbox to Tackle the Curse of Imbalanced Datasets in Machine Learning. *arXiv.* 2016. https://doi.org/10.48550/ARXIV.1609.06570
