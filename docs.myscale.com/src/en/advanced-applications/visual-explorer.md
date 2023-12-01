# Visual Dataset Explorer

<a href="https://huggingface.co/spaces/myscale/visual-dataset-explorer"  style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-orange"></a>

Modern datasets always contain millions of unstructured data like images, audio clips and even videos. Querying nearest neighbours in such datasets are challenging: 1. Measuring distances among unstructured data is ambiguous; 2. Sorting data regarding billions of distances also needs extra effort. Fortunately, the first barrier has been flattened by recent research like [CLIP](https://openai.com/blog/clip/), and the second can be boosted by advanced vector search algorithms. MyScale provides a unified database solution to DB+AI applications, enabling high-performance search among large datasets. In this example, we will demonstrate how a DB+AI application can be built by training a fine-grained classifier using the hard-negative mining technique.

In this demo, we adopted [unsplash-25k Dataset](https://github.com/unsplash/datasets), a dataset containing about 25 thousand images, as our playground. Its photos cover complicated scenes and objects.

## Why are we working with a database?

To someone who asked about the role of the database, I need to dive a little deeper into some AI stuff. We all know that a conventional Classifier always asks for tons of data, annotations and bags of training tricks to obtain high accuracy in real life. Those are sufficient but not actually necessary to get an accurate classifier. A closer guess will help us to get to the optimum faster. Thanks to CLIP, we can now obtain a good starting point for the classifier. And the only thing left to us is to focus on examples that are similar but not the same, which refers to the hard-negative mining technique in the AI term. Now it is time for a vector database, e.g., MyScale, to shine.

MyScale is a vector database that supports high-performance searches among billions of vectors. Costly operations like hard-negative mining will never be an obstacle to AI applications and research with MyScale. Finding hard negatives only takes milliseconds. So the whole fine-tuning process can only take **within a few clicks** on the webpage.

## How to play with the demo？

<video controls loop autoplay muted preload="auto">
  <source src="https://myscale-demo.s3.ap-southeast-1.amazonaws.com/visual-dataset-explorer/demo_compressed.mp4" type="video/mp4">
</video>

Why not try out [our online demo](https://huggingface.co/spaces/myscale/visual-dataset-explorer)?

## Installing Prerequisites

* `transformers`: Running CLIP model
* `tqdm`: Beautiful progress bar for humans
* `clickhouse-connect`: MyScale database client
* `streamlit`: Python web server to run the app

```bash
python3 -m pip install transformers tqdm clickhouse-connect streamlit pandas lmdb torch

```

You can download metadata if you want to build your own database.

```bash
# Downloads Unsplash 25K Dataset 
wget https://unsplash-datasets.s3.amazonaws.com/lite/latest/unsplash-research-dataset-lite-latest.zip
# Unzip it...
unzip unsplash-research-dataset-lite-latest.zip
# You will have a file called `photos.tsv000` in your current working directory
# Then you can extract the CLIP feature from the dataset
```

## Building a Database with Vectors

### Getting Into the Data

First, let's look into the structure of the Unsplash-25k Dataset. File `photos.tsv000` contains metadata and annotation for all images in the dataset. A single row of it looks like this:

|photo_id|photo_url|photo_image_url|...|
|:----|:-------|:-----|:----|
|xapxF7PcOzU|https://unsplash.com/photos/xapxF7PcOzU|https://images.unsplash.com/photo-1421992617193-7ce245f5cb08|...|

The first column refers to the unique identifier for this image. The next column is the URL to its description page, telling its author and other meta information. The third column contains the image URLs. Image URLs can be directly used to retrieve the image with [unsplash API](https://unsplash.com/documentation#example-image-use). Here is an example of the `photo_image_url` column mentioned above:

![Special thanks to the `unsplash.com` and the photo author Timothy Kolczak](https://images.unsplash.com/photo-1421992617193-7ce245f5cb08?q=75&fm=jpg&w=400&fit=max)

So we use the code below to load the data:

```python
import pandas as pd
from tqdm import tqdm
images = pd.read_csv(args.dataset, delimiter='\t')
```

### Creating a MyScale Database Table

#### Working with the database

You need a connection to a database backend to create a table in MyScale. You can check out the detailed guide on python client on [this page](../python-client.md#creating-connection).

If you are familiar with SQL (Structured Query Language), it would be much easier for you to work with MyScale. MyScale combines the structured query with vector search, which means creating a vector database is exactly the same as creating conventional databases. And here is how we create a vector database in SQL:

```sql
CREATE TABLE IF NOT EXISTS unsplash_25k(
        id String,
        url String,
        vector Array(Float32),
        CONSTRAINT vec_len CHECK length(vector) = 512
        ) ENGINE = MergeTree ORDER BY id;
```

We define the image's `id` as strings, `url`s as strings and feature vectors `vector` as a fixed length array with a datatype of 32 bits floating number and dimension of 512. In another word, a feature vector of an image contains 512 32-bits float numbers. We can execute this SQL with the connection we just created:

```python
client.command(
"CREATE TABLE IF NOT EXISTS unsplash_25k (\
        id String,\
        url String,\
        vector Array(Float32),\
        CONSTRAINT vec_len CHECK length(vector) = 512\
) ENGINE = MergeTree ORDER BY id")
```

### Extracting Features and Fill the Database

[CLIP](https://openai.com/blog/clip/) is a popular method that matches data from different forms (or we adopt the academic term "modal") into a unified space, enabling high-performance cross-modal retrieval. For example, you can use the feature vector of a phase "a photo of a house by a lake" to search for similar photos and vice versa.

Several hard negative mining steps can train an accurate classifier using a zero-shot classifier as an initialization. We can take a CLIP vector generated from the text as our initial parameter for the classifier. Then we can proceed to the hard negative mining part: searching all similar samples and excluding all negative ones. Here is a code example that demonstrates how to extract features from a single image:

```python
from torch.utils.data import DataLoader
from transformers import CLIPProcessor, CLIPModel
model_name = "openai/clip-vit-base-patch32"

# You might need several minutes to download the CLIP Model
model = CLIPModel.from_pretrained(model_name).to(device)
# The processor will preprocess the image
processor = CLIPProcessor.from_pretrained(model_name)

# Using the data we just loaded in the previous section
row = images.iloc[0]
# Get the URL and unique identifier of the image
url = row['photo_image_url']
_id = row['photo_id']

import requests
from io import BytesIO
# Download the image and load it
response = requests.get(url)
img = Image.open(BytesIO(response.content))
# Preprocess the image and return a PyTorch Tensor
ret = self.processor(text=None, images=img, return_tensor='pt')
# Get the image values
img = ret['pixel_values']
# Get the feature vector (float32, 512d)
out = model.get_image_features(pixel_values=img)
# Normalize the vector before insert to the DB
out = out / torch.norm(out, dim=-1, keepdims=True)
```

By now we have already collected all data we need to construct the table. There is only one piece left in this puzzle: inserting data into MyScale. For detailed `INSERT` clause usage, you can refer to [SQL reference](../quickstart.md#importing-data).

```python
# A showcase for inserting a single row into the table

# You need to convert the feature vector into python lists
transac = [_id, url, out.cpu().numpy().squeeze().tolist()]
# just insert the vector as a normal SQL
client.insert("unsplash_25k", transac)
```

## Few-shot Learning on Classifier

### Initializing the Classifier Parameters

As we discussed above, we can use the text feature to initialize our classifier.

```python
from transformers import CLIPTokenizerFast, CLIPModel
# Initialize the Tokenizer
tokenizer = CLIPTokenizerFast.from_pretrained(model_name)

# Input anything you want to search
prompt = 'a house by the lake'
# get the tokenized prompt and its feature
inputs = tokenizer(prompt, return_tensors='pt')
out = model.get_text_features(**inputs)
xq = out.squeeze(0).cpu().detach().numpy().tolist()
```

With the text feature vector, we can get an approximate centroid of images we desired, which will be the classifier's initial parameter. Hence, a classifier class can be defined as:

```python
DIMS = 512
class Classifier:
    def __init__(self, xq: list):
        # initialize model with DIMS input size and 1 output
        # note that the bias is ignored, as we only focus on the inner product result
        self.model = torch.nn.Linear(DIMS, 1, bias=False)
        # convert initial query `xq` to tensor parameter to init weights
        init_weight = torch.Tensor(xq).reshape(1, -1)
        self.model.weight = torch.nn.Parameter(init_weight)
        # init loss and optimizer
        self.loss = torch.nn.BCEWithLogitsLoss()
        self.optimizer = torch.optim.SGD(self.model.parameters(), lr=0.1)
```

Recalling $Y=\sigma(XW)$, for $X\in\mathbb{R}^n$, $W\in\mathbb{R}^n$ and $Y\in\mathbb{R}$, a linear classifier with activation function is exactly the same to the similarity metric for CLIP -- doing a mapped simple inner product. So you can treat the output $Y$ as the similarity score given the input vector $X$ and the decision vector $W$. Of course, you can use the text feature which is close to the queried images as the initial parameter for the classifier. Moreover, the `BCEwithLogitsLoss` (Binary Cross Entropy Loss) is for pushing negative samples away and pulling the decision vector to positive samples. This will give you an intuitive sense of what is happening at the AI part.

### Getting Similar Samples with DB

Finally, we built the vector database with MyScale and the classifier with our text prompt. Now we can use its similarity search function to perform hard-negative mining on the classifier. But first, we need to tell the database which metric the features used to measure similarity.

MyScale provides many different algorithms to accelerate your search on various metrics. Common metrics like `L2`, `cosine` and `IP` are supported. In this example, we follow the CLIP setup and choose the cosine distance as our metric to search nearest neighbours and use an approximated nearest neighbour searching algorithm called `MSTG` to index our feature.

```sql
-- We create a vector index vindex on the vector column
-- with the parameter of `metric` and `ncentroids`
ALTER TABLE unsplash_25k ADD VECTOR INDEX vindex vector TYPE MSTG('metric_type=Cosine')
```

Once [the vector index is built](../vector-search.md#checking-the-status-of-vector-indexes), we can now search using the operator `distance` to perform the nearest neighbour retrieval.

```sql
-- Please note that the query vector should be converted to a string before being executed
SELECT id, url, vector, distance(vector, <query-vector>) AS dist FROM unsplash_25k ORDER BY dist LIMIT 9
```

> Please note: for any SQL verbs that return values like `SELECT`, you need to use `client.query()` to retrieve the result.

And also you can perform a mixed query that filters out unwanted rows:

```sql
SELECT id, url, vector, distance(vector, <query-vector>) AS dist
        FROM unsplash_25k WHERE id NOT IN ('U5pTkZL8JI4','UvdzJDxcJg4','22o6p17bCtQ', 'cyPqQXNJsG8')
        ORDER BY dist LIMIT 9
```


Assuming we named the SQL sentence above into a string `qstr`, then the query in python can be done like this:

```python
q = client.query(qstr).named_results()
```

Returned `q` has multiple dictionary-like objects. In this case, we have 9 returned objects as we requested top-9 nearest neighbours. We can use column names to retrieve values from each element of `q`. For example, if we want to get all ids and their distance to the query vector, we can code like this in Python:

```python
id_dist = [(_q["id"], _q["dist"]) for _q in q]
```

### Fine-tuning the Classifier

With the power of MyScale, we can now retrieve the nearest neighbours in DB within a blink. The final step of this app will be tuning the classifier regarding the user's supervision.

I would omit the UI design step because it is too narrative to write in this blog :P I will go straight to the point when the model training happens.

```python
# NOTE: Please Add this to the Previous Classifier
def fit(self, X: list, y: list, iters: int = 5):
# convert X and y to tensor
X = torch.Tensor(X)
y = torch.Tensor(y).reshape(-1, 1)
for i in range(iters):
    # zero gradients
    self.optimizer.zero_grad()
    # Normalize the weight before inference
    # This will constrain the gradient or you will have an explosion on the query vector
    self.model.weight.data = self.model.weight.data / torch.norm(self.model.weight.data, p=2, dim=-1)
    # forward pass
    out = self.model(X)
    # compute loss
    loss = self.loss(out, y)
    # backward pass
    loss.backward()
    # update weights
    self.optimizer.step()
```

The code above gives you a few-shot learning pipeline to train the existing classifier. With only a few images annotated, the classifier can converge and give you impressive accuracy to the concept in your mind. 

The training process is trivial. First, we recall that the weight vector is generally an indicator that measures the similarity between the query and the desired. You can consider it as a centroid of a cone of a sphere with the classifier parameter as its directional vector and the score threshold as its radius. Everything inside the cone will be treated as positive, while the outside is negative. Training steps will push the vector to cover as many positives as possible and away from the negatives. Continuing with the cone vector theory, we only need a normed vector to describe the centroid of the cone. So we need to normalize the learned parameter after every iteration. We can also think in another way: the positives, which are un-normalized vectors, will pull the centroid towards their positions, and we might end up with a vector that is very long in magnitude but poor in describing direction among the positives. It will degrade the performance of the similarity search. Normalizing the vector will only keep the perpendicular component of the gradient. This will stabilise our visual result in our demo.

## In the End

In this demo, we reviewed how to build a demo that trains a few-shot learned classifier with MyScale. More importantly, we also introduced how to use MyScale to store, index and search using extended SQL with its advanced vector search engine. Hope you enjoy this blog!

References:

1. MultiLingual CLIP: <https://huggingface.co/M-CLIP/XLM-Roberta-Large-Vit-B-32>
2. CLIP: <https://huggingface.co/openai/clip-vit-base-patch32>
3. Unsplash 25K Dataset: <https://github.com/unsplash/datasets>
