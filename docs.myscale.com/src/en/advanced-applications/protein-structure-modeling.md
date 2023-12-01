# Protein Structure Modeling

<a href="https://huggingface.co/spaces/myscale/Protein-Structure-Modeling"  style='padding-left: 0.5rem;'><img src='https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-orange'></a>

## Background

Proteins, encoded by our genes, are the fundamental building blocks of life and exhibit complexity and dynamism. They perform a wide range of functions, such as detecting light for sight, fighting off viruses through antibodies, and powering motion in microbes and muscles. Our goal is to analyze protein structure to better understand their intricate composition and functions, allowing us to shed light on the intricacies of life and make advances in fields such as biochemistry, medicine, and biotechnology. Specifically in this demo, we leverage vector representations from state-of-the-art protein language models with MyScale database for similar protein search and protein activity prediction.

## How to play with the demo?

![demo](https://myscale-demo.s3.ap-southeast-1.amazonaws.com/protein_demo/combine.gif)

## Method

So far, protein language models have focused on analyzing individual sequences for inference. Traditionally, computational biology relies on fitting separate models for each family of related sequences. Our demo utilizes the [ESMFold](https://github.com/facebookresearch/esm) model to encode a 12 million protein sequence dataset and perform vector search using the MyScale database, making it simple to carry out tasks such as protein search and predicting biological activity.

### Protein Encoder

ESMFold is an evolutionary scale language model that predicts protein structure by assigning a probability to each amino acid at every position in a protein based on its context in the rest of the sequence. Vector representation is a key component of ESMFold as it serves as a universal encoding for the protein sequence. The model uses this representation to capture the contextual information of each amino acid in the sequence, and the relationships between different amino acids. This allows ESMFold to generate a probability distribution over the potential structures of a protein from a single input sequence. By leveraging the masked language modeling objective during training, ESMFold has learned to generate more accurate predictions, leading to improved protein structure prediction performance.

### Vector Search with MyScale

MyScale combines the power of SQL and vector databases to deliver high-speed searches on billions of vectors. The latest search algorithms eliminate the challenges of similar example and hard negative mining. Hard negatives are found in just milliseconds and classifier training is now just a few clicks away on the web page, saving you time and reducing costs for your AI applications. Furthermore, its improved data management, implemented through hybrid SQL vector queries, significantly speeds up your research and development process.

### Application in Protein Search and Activity Prediction

In this demo, we showcase two applications: protein search and prediction of protein activity. The latter involves forecasting the biological impact of protein mutations using pre-defined embeddings from ESM. Both applications make use of vector search in MyScale.

## Installing Prerequisites

This demo is primarily constructed using the following libraries, among others:

* `transformers`: Running ESMFold model
* `clickhouse-connect`: Database client
* `streamlit`: Python web server to run the app

To install the necessary prerequisites, use the following command:

```bash
python3 -m pip install -r requirement.txt
```

You can download the data via fasta files in <https://github.com/facebookresearch/esm#bulk_fasta>, using the following command:

```bash
python esm/scripts/extract.py esm2_t33_650M_UR50D examples/data/some_proteins.fasta \
  examples/data/some_proteins_emb_esm2 --repr_layers 0 32 33 --include mean per_tok
```

## Building a Database with Vectors

### Check the Data

Let’s look into the structure of fasta files. File `P62593.fasta` contains protein sequence and activity in a row and looks like this:

```text
id>protein name>activity>protein sequence
>0|beta-lactamase_P20P|1.581033423 > MSIQHFRVALIPFFAAFCLPVFAHPETLVKVKDAEDQLGARVGYIELDLNSGKILESFRPEERFPMMSTFKVLLCGAVLSRVDAGQEQLGRRIHYSQNDLVEYSPVTEKHLTDGMTVRELCSAAITMSDNTAANLLLTTIGGPKELTAFLHNMGDHVTRLDRWEPELNEAIPNDERDTTMPAAMATTLRKLLTGELLTLASRQQLIDWMEADKVAGPLLRSALPAGWFIADKSGAGERGSRGIIAALGPDGKPSRIVVIYTTGSQATMDERNRQIAEIGASLIKHW
```

By following the data format we have just analyzed, those meta info can be easily obtained with pysam:

```python
from pysam import FastaFile
fasta = "P62593.fasta"
# read FASTA file
sequences_object = FastaFile(fasta)
```

### Creating a MyScale Table

Before you proceed, you will need a valid credential to login our database engine. Please check out the detailed guide on python client on [this page](../python-client.md#creating-connection) to learn how to login in.

Here is how the table structure look like in SQL:

```python
CREATE TABLE esm_protein_indexer
( 
    id UInt64,
    activity Float32,
    seq String, 
    representations Array(Float32),
    CONSTRAINT representations CHECK length(vector) = 768
) 
```

### Extracting Features and Fill the DB

The ESM model boasts a zero-shot capability and excels in extracting semantic features from protein sequences. It offers both single protein feature extraction and batch processing methods. The implementation code is presented as follows.

```python
import torch
import esm
# Load ESM-2 model
model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
batch_converter = alphabet.get_batch_converter()model.eval()  # disables dropout for deterministic results
# Prepare data (first 2 sequences from ESMStructuralSplitDataset superfamily / 4)
data = [
    ("protein1", "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"),
    ("protein2", "KALTARQQEVFDLIRDHISQTGMPPTRAEIAQRLGFRSPNAAEEHLKALARKGVIEIVSGASRGIRLLQEE"),
    ("protein2 with mask","KALTARQQEVFDLIRD<mask>ISQTGMPPTRAEIAQRLGFRSPNAAEEHLKALARKGVIEIVSGASRGIRLLQEE"),
    ("protein3",  "K A <mask> I S Q"),
]
batch_labels, batch_strs, batch_tokens = batch_converter(data)
batch_lens = (batch_tokens != alphabet.padding_idx).sum(1)
# Extract per-residue representations (on CPU)
with torch.no_grad():
    results = model(batch_tokens, repr_layers=[33], return_contacts=True)
    token_representations = results["representations"][33]
```

We can also extracts embeddings in bulk from a FASTA file.

```bash
python scripts/extract.py esm2_t33_650M_UR50D examples/data/some_proteins.fasta \
  examples/data/some_proteins_emb_esm2 --repr_layers 0 32 33 --include mean per_tok
```

We have already accomplished a zero shot learning pipeline with the protein sequence feature as the classifier. By now I think we are pretty close to constructing the table. There is only one piece left in this puzzle: inserting data into MyScale. Here is how it looks like:

```python
# You need to convert the feature vector into python lists
fields = ['id', 'seq','representations','activity']
# just insert the vector as normal SQL
client.insert("esm_protein_indexer_768", data, column_names=fields)
```

For detailed `INSERT` clause usage, you can refer to Official Documentation.

## Protein Search

To search using protein embeddings obtained from the ESM model, we extract the embedding of the query sequence and use SQL to locate the embeddings of the five closest protein sequences in MyScale. The result is then returned.

```python
def esm_search(client, model, sequnce, batch_converter, top_k=5):
    data = [("protein1", sequnce)]
    batch_labels, batch_strs, batch_tokens = batch_converter(data)

    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=True)
    token_representations = results["representations"][33]
    token_list = token_representations.tolist()[0][0][0]
        
    query = f"SELECT activity, distance(representations, {token_list}) as dist "
    query += "FROM default.esm_protein_indexer_768"
    query += f" ORDER BY dist LIMIT {top_k}"
    result = client.query(query).named_results()

    result_temp_coords = [i['coords'] for i in result]
    result_temp_seq = [i['seq'] for i in result]

    return result_temp_coords, result_temp_seq
```

## KNN for Activity Prediction

The KNN method predicts the current protein's activity by using the average of the activities of the 10 nearest neighbors. This approach doesn't require additional training and tuning and has relatively high accuracy.

Data in myscale contains:

* the mutated ß-lactamase sequence, where a single residue is mutated (swapped with another amino acid)
* the target value in the last field of the header, describing the scaled effect of the mutation

Here is how the function looks like:

```python
def knn_search(client, sequence):
    model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
    batch_converter = alphabet.get_batch_converter()
    model.eval()
    data = [("protein1", sequence)]
    batch_labels, batch_strs, batch_tokens = batch_converter(data)
    batch_lens = (batch_tokens != alphabet.padding_idx).sum(1)

    with torch.no_grad():
        results = model(batch_tokens, repr_layers=[33], return_contacts=True)
    token_representations = results["representations"][33]
    token_list = token_representations.tolist()[0][0]

    result = client.query(f"SELECT activity, distance(representations, {token_list}) as dist FROM default.esm_protein_indexer ORDER BY dist LIMIT 10").named_results()
    activity_sum = sum(i['activity'] for i in result)
    avg_activity = activity_sum / len(result)
    return avg_activity
```

## In the End

References:

1. Evolutionary Scale Modeling:  <https://github.com/facebookresearch/esm>
2. KNN: <https://towardsdatascience.com/machine-learning-basics-with-the-k-nearest-neighbors-algorithm-6a6e71d01761>
