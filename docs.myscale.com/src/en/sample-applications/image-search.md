# Image Search

<a href="https://colab.research.google.com/github/myscale/examples/blob/main/image-search.ipynb" style="padding-left: 0.5rem;"><img src="https://colab.research.google.com/assets/colab-badge.svg?style=plastic)](https://colab.research.google.com/github/myscale/examples/blob/main/image-search.ipynb)"></a>
<a href="https://github.com/myscale/examples/blob/main/image-search.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/myscale/examples/blob/main/image-search.ipynb)"></a>

## Introduction

Image search has become a popular and powerful application, enabling users to find similar images by matching features or visual content. With the rapid development of computer vision and deep learning, this capability has been greatly enhanced.

This guide is designed to help you leverage the latest techniques and tools for image search. In this guide, you will learn how to:
* Create a dataset with vector embeddings using a public dataset and model
* Perform image similarity search with MyScale, a powerful platform that streamlines the search process and provides fast and accurate results

If you're more interested in exploring capabilities of MyScale, feel free to skip the [Building dataset](#building-dataset) section and dive right into the [Populating data to MyScale](#populating-data-to-myscale) section.

You can import this dataset on the MyScale console by following the instructions provided in the [Import data](../cluster-management/index.md#import-data) section for the **Image Search** dataset. Once imported, you can proceed directly to the [Querying MyScale](#querying-myscale) section to enjoy this sample application.

## Prerequisites

Before we get started, we need to install the [clickhouse python client](https://clickhouse.com/docs/en/integrations/language-clients/python/intro/) and the HuggingFace `datasets` library to download sample data.

```bash
pip install datasets clickhouse-connect
```

To follow along with the steps outlined in the [Building dataset](#building-dataset) section, we need to install transformers and other necessary dependencies.

```bash
pip install requests transformers torch tqdm
```

## Building Dataset

### Downloading and Processing Data

We download data from [unsplash dataset](https://github.com/unsplash/datasets) and we use the Lite dataset.

```bash
wget https://unsplash-datasets.s3.amazonaws.com/lite/latest/unsplash-research-dataset-lite-latest.zip

# unzip the downloaded files into a temporary directory
unzip unsplash-research-dataset-lite-latest.zip -d tmp
```

We read the downloaded data and transform it into Pandas dataframes.

```python
import numpy as np
import pandas as pd
import glob

documents = ['photos', 'conversions']
datasets = {}

for doc in documents:
    files = glob.glob("tmp/" + doc + ".tsv*")
    subsets = []
    for filename in files:
        df = pd.read_csv(filename, sep='\t', header=0)
        subsets.append(df)
    datasets[doc] = pd.concat(subsets, axis=0, ignore_index=True)

df_photos = datasets['photos']
df_conversions = datasets['conversions']
```

### Generating Image Embeddings

To extract embeddings from images, we define an `extract_image_features` function that utilizes the [clip-vit-base-patch32](https://huggingface.co/openai/clip-vit-base-patch32) model from HuggingFace. The resulting embeddings are 512-dimensional vectors.

```python
import torch
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def extract_image_features(image):
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
        outputs = outputs / outputs.norm(dim=-1, keepdim=True)
    return outputs.squeeze(0).tolist()
```

After that, we select the first 1000 photo IDs from the `df_photos` data frame, download the corresponding images, and extract their image embeddings using the extract_image_features function.

```python
from PIL import Image
import requests
from tqdm.auto import tqdm

# select the first 1000 photo IDs
photo_ids = df_photos['photo_id'][:1000].tolist()

# create a new data frame with only the selected photo IDs
df_photos = df_photos[df_photos['photo_id'].isin(photo_ids)].reset_index(drop=True)

# keep only the columns 'photo_id' and 'photo_image_url' in the data frame
df_photos = df_photos[['photo_id', 'photo_image_url']]

# add a new column 'photo_embed' to the data frame
df_photos['photo_embed'] = None

# download the images and extract their embeddings using the 'extract_image_features' function
for i, row in tqdm(df_photos.iterrows(), total=len(df_photos)):
    # construct a URL to download an image with a smaller size by modifying the image URL
    url = row['photo_image_url'] + "?q=75&fm=jpg&w=200&fit=max"

    try:
        res = requests.get(url, stream=True).raw
        image = Image.open(res)
    except:
        # remove photo if image download fails
        photo_ids.remove(row['photo_id'])
        continue

    # extract feature embedding
    df_photos.at[i, 'photo_embed'] = extract_image_features(image)
```

### Creating Dataset

We now have two data frames: one for photo information with embeddings and the other for conversion information.

```python
df_photos = df_photos[df_photos['photo_id'].isin(photo_ids)].reset_index().rename(columns={'index': 'id'})

df_conversions = df_conversions[df_conversions['photo_id'].isin(photo_ids)].reset_index(drop=True)
df_conversions = df_conversions[['photo_id', 'keyword']].reset_index().rename(columns={'index': 'id'})
```

Finally, we convert the dataframes into Parquet files and then proceed to upload them to the Hugging Face repository [myscale/unsplash-examples](https://huggingface.co/datasets/myscale/unsplash-examples) by following the [steps](https://huggingface.co/docs/datasets/upload_dataset). This facilitates easy access and sharing of the data.

```python
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np

# create a Table object from the data and schema
photos_table = pa.Table.from_pandas(df_photos)
conversion_table = pa.Table.from_pandas(df_conversions)

# write the table to a Parquet file
pq.write_table(photos_table, 'photos.parquet')
pq.write_table(conversion_table, 'conversions.parquet')
```

## Populating Data to MyScale

### Loading Data

To populate data to MyScale, first, we load data from the HuggingFace Dataset [myscale/unsplash-examples](https://huggingface.co/datasets/myscale/unsplash-examples) created in the previous section. The following code snippet shows how to load data and transform them into panda DataFrames.

Note: `photo_embed` is a 512-dimensional floating-point vector that represents the image features extracted from an image using the [CLIP](https://huggingface.co/openai/clip-vit-base-patch32) model.

```python
from datasets import load_dataset

photos = load_dataset("myscale/unsplash-examples", data_files="photos-all.parquet", split="train")
conversions = load_dataset("myscale/unsplash-examples", data_files="conversions-all.parquet", split="train")

# transform datasets to panda Dataframe
photo_df = photos.to_pandas()
conversion_df = conversions.to_pandas()

# convert photo_embed from np array to list
photo_df['photo_embed'] = photo_df['photo_embed'].apply(lambda x: x.tolist())
```

### Creating Table

Next, we create tables in MyScale. Before you begin, you will need to retrieve your cluster host, username, and password information from the MyScale console. The following code snippet creates two tables, one for photo information and the other for conversion information.

```python
import clickhouse_connect

# initialize client
client = clickhouse_connect.get_client(host='YOUR_CLUSTER_HOST', port=443, username='YOUR_USERNAME', password='YOUR_CLUSTER_PASSWORD')

# drop table if existed
client.command("DROP TABLE IF EXISTS default.myscale_photos")
client.command("DROP TABLE IF EXISTS default.myscale_conversions")

# create table for photos
client.command("""
CREATE TABLE default.myscale_photos
(
    id UInt64,
    photo_id String,
    photo_image_url String,
    photo_embed Array(Float32),
    CONSTRAINT vector_len CHECK length(photo_embed) = 512
)
ORDER BY id
""")

# create table for conversions
client.command("""
CREATE TABLE default.myscale_conversions
(
    id UInt64,
    photo_id String,
    keyword String
)
ORDER BY id
""")
```

### Uploading Data

After creating the tables, we insert data loaded from the datasets into tables and create a vector index to accelerate later vector search queries. The following code snippet shows how to insert data into tables and create a vector index with cosine distance metric.

```python
# upload data from datasets
client.insert("default.myscale_photos", photo_df.to_records(index=False).tolist(),
              column_names=photo_df.columns.tolist())
client.insert("default.myscale_conversions", conversion_df.to_records(index=False).tolist(),
              column_names=conversion_df.columns.tolist())

# check count of inserted data
print(f"photos count: {client.command('SELECT count(*) FROM default.myscale_photos')}")
print(f"conversions count: {client.command('SELECT count(*) FROM default.myscale_conversions')}")

# create vector index with cosine
client.command("""
ALTER TABLE default.myscale_photos 
ADD VECTOR INDEX photo_embed_index photo_embed
TYPE MSTG
('metric_type=Cosine')
""")

# check the status of the vector index, make sure vector index is ready with 'Built' status
get_index_status="SELECT status FROM system.vector_indices WHERE name='photo_embed_index'"
print(f"index build status: {client.command(get_index_status)}")
```

## Querying MyScale

### Finding Top K Similar Images

To find the top K similar images using vector search, follow these steps:

First, let's randomly select an image and display it using the show_image() function.

```python
import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

# download image with its url
def download(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# define a method to display an online image with a URL
def show_image(url, title=None):
    img = download(url)
    fig = plt.figure(figsize=(4, 4))
    plt.imshow(img)
    plt.show()

# display the number of rows in each table
print(f"photos count: {client.command('SELECT count(*) FROM default.myscale_photos')}")
print(f"conversions count: {client.command('SELECT count(*) FROM default.myscale_conversions')}")

# pick a random image from the table as the target
random_image = client.query("SELECT * FROM default.myscale_photos ORDER BY rand() LIMIT 1")
assert random_image.row_count == 1
target_image_id = random_image.first_item["photo_id"]
target_image_url = random_image.first_item["photo_image_url"]
target_image_embed = random_image.first_item["photo_embed"]
print("currently selected image id={}, url={}".format(target_image_id, target_image_url))

# display the target image
print("Loading target image...")
show_image(target_image_url)
```

A sample image:

<div style="text-align: left; min-width: 600px;">
<img src="../../assets/sample-applications/image-search/image1.jpg" width=40%>
</div>

Then, use vector search to identify the top K candidates that are most similar to the selected image, and display these candidates:

```python
# query the database to find the top K similar images to the given image
top_k = 10
results = client.query(f"""
SELECT photo_id, photo_image_url, distance(photo_embed, {target_image_embed}) as dist
FROM default.myscale_photos
WHERE photo_id != '{target_image_id}'
ORDER BY dist
LIMIT {top_k}
""")

# download the images and add them to a list
images_url = []
for r in results.named_results():
    # construct a URL to download an image with a smaller size by modifying the image URL
    url = r['photo_image_url'] + "?q=75&fm=jpg&w=200&fit=max"
    images_url.append(download(url))

# display candidate images
print("Loading candidate images...")
for row in range(int(top_k / 5)):
    fig, axs = plt.subplots(1, 5, figsize=(20, 4))
    for i, img in enumerate(images_url[row * 5:row * 5 + 5]):
        axs[i % 5].imshow(img)
    plt.show()
```

Similar candidate images:

<div style="text-align: left; min-width: 600px;">
<img src="../../assets/sample-applications/image-search/image2.jpg">
</div>

### Analyzing Conversion Information for each Candidate Image

After identifying the top K similar images, you can use SQL queries combining structured fields and vector fields to perform analysis on the conversion information for each candidate.

To calculate the total conversion count for each candidate image, you can use the following SQL query to join the image search results with the `conversions` table:

```python
# show the total download count for each candidate image
results = client.query(f"""
SELECT photo_id, count(*) as count
FROM default.myscale_conversions
JOIN (
    SELECT photo_id, distance(photo_embed, {target_image_embed}) as dist
    FROM default.myscale_photos
    ORDER BY dist ASC
    LIMIT {top_k}
    ) AS target_photos
ON default.myscale_conversions.photo_id = target_photos.photo_id
GROUP BY photo_id
ORDER BY count DESC
""")

print("Total downloads for each candidate")
for r in results.named_results():
    print("- {}: {}".format(r['photo_id'], r['count']))
```

Sample output:

```text
Total downloads for each candidate
- Qgb9urMZ8lw: 1729
- f0OL01IHbCM: 1444
- Bgae-sqbe_g: 313
- XYg2zLjxxa0: 207
- BkW8I1n354I: 184
- 5yFOvJZp7Rg: 63
- sKPPBn6OkJg: 48
- joL0nSbZ-lI: 20
- fzDtQWW8dV4: 8
- DCAERnaj31U: 3
```

After calculating the total conversion count for each candidate image, you can identify the candidate image with the most downloads, and examine the detailed conversion information per download keyword for that image. Use the following SQL query:

```python
# display the the most popular candidate and the top 5 related download keywords
most_popular_candidate = results.first_item['photo_id']

# display most popular image
candidate_url = client.command(f"""
SELECT photo_image_url FROM default.myscale_photos WHERE photo_id = '{most_popular_candidate}'
""")

print("Loading the most popular candidate image...")
show_image(candidate_url)

# find top-5 download keywords
results = client.query(f"""
SELECT keyword, count(*) as count
FROM default.myscale_conversions
WHERE photo_id='{most_popular_candidate}'
GROUP BY keyword
ORDER BY count DESC
LIMIT 5
""")

print("Related keywords and download counts for most popular candidate")
for r in results.named_results():
    print(f"- {r['keyword']}: {r['count']}") 
```

The most popular candidate image in top10:
<div style="text-align: left; min-width: 600px;">
<img src="../../assets/sample-applications/image-search/image3.jpg" width=40%>
</div>

Sample output:

```text
Related keywords and download counts for most popular candidate
- bee: 1615
- bees: 21
- bumblebee: 13
- honey: 13
- honey bee: 12
```
