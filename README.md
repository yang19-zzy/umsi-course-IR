# Improve How Students Search for Courses
(tl;dr)
This project uses Pyterrier to index documents(course descriptions) and retrieve top 10 most relevant courses with Wikipedia collection indexing and its query expansion.


## I - Project Intention
This project is originally a course project from UMSI 650 - Information Retrieval. Based on our own experience as students, we know that students are struggling with choosing the right courses for themselves, especially when they are still unsure about their future career path and want to try anything they're interested in.

For students from the University of Michigan, they are able to use [Atlas](https://atlas.ai.umich.edu/) to look up a specific course and the course evaluation. Although the returned results also show what other courses that peers were taking in the same semester or previsous semesters, students, still, need to know the course names first, which sometimes is a bumper for students really want to do their search.

Therefore, we want to use the knowledge learned from the course to build a course search enginee by ourselves. 🤓

## II - Data
### Data Resource & Collection
The data we used for this project is from [UMSI course website](https://www.si.umich.edu/programs/courses). We collected all courses it has, including course number, course name, and course description. As long as there is a course number or course code, no matter whether the course names are the same, each of them is considered as a separate file. We wrote each pair of course name and course description to a document and stored it as `.txt` file.

### Data Description
There are total 120 courses under UMSI. We have 120 `.txt` files stored in Google Drive.

### Data Preprocessing
We created three DataFrames that we will need for the next step indexing.

1. Document dataframe

docno | abstract
---|---
si_106 | 106 - Programs, Information and People ...
... | ...
  
2. Query dataframe

qid | query
--- | ---
1 | R programming
... | ...

3. Annotated dataframe

qid | query | docno | abstract | label
---| ---| --- | --- | --- 
1 | R programming | si_106 | 106 - Programs, Information and People ... | 3
...|...|...|...|...


#### Annotation
We used BM25 to retrieve top 50 most relevant courses for 20 queries and labeled these results with 5 points scale. Based on how query and course description related, we gave 5 to most related results and 1 to least related or not related.

Here is how these query-doc pair distribute after annotation.

![Number of Query-Doc Pairs in Each Relevant Level](https://github.com/yang19-zzy/umsi-course-IR/blob/main/image/barplot1.png)


Also, since we didn't annotate all documents, the rest of query-doc pair we considered them having relation level 1.

Here is how filled-with-1 query-doc pair distribute.

![Number of Query-Doc Pairs in Each Relevant Level (fillna)](https://github.com/yang19-zzy/umsi-course-IR/blob/main/image/barplot2.png)


## III - Indexing
We used [Pyterrier](https://pyterrier.readthedocs.io/en/latest/installation.html) to fulfill our indexing need with the following code.
```
import pyterrier as pt
if not pt.started():
    pt.init()

pt_index_path = './index/iterdictindex'
if not os.path.exists(pt_index_path + "/data.properties"):
    indexer = pt.IterDictIndexer(pt_index_path, blocks=True)
    index_ref = indexer.index(df_doc.to_dict(orient="records"), fields=('docno', 'abstract'))
else:
    index_ref = pt_index_path + "/data.properties"
index = pt.IndexFactory.of(index_ref)
```
Here, we used [IterDictIndexer](https://pyterrier.readthedocs.io/en/latest/terrier-indexing.html#iterdictindexer), which because our preprocessed data is dataframe that can be iterated through, and also because it is much faster at transfering data since it used multiple threads and POSIX fifos.

### Other Indexings
We tried to used other aproaches to get indexing as well.
1. Wikipedia collection

Since our origin data is limited and there're only 120 documents overall, we tried to make sure the index we have can handle more complicated tasks like query expansion. Therefore, we downloaded Wikipedia collection from [Pyterrier Dataset](https://pyterrier.readthedocs.io/en/latest/datasets.html#available-datasets) and did indexing in the same way we did for our original data.

2. Doc2query

Besides, we want to try **doc2query** that mentioned in the class and wonder how this technique could have an impact on retrived documents. So, we downloaded the pretrained model with t5-base that provided by our [professor David](https://jurgens.people.si.umich.edu/). 😎  Then we used this pretrained model to generate question-like query and appended query back to document.

And the code for the **Indexer** will be something like this:
```
indexer = (
    pyterrier_doc2query.Doc2Query('model.ckpt-1004000', doc_attr='abstract', batch_size=8, append=True)
    >> pt.apply.generic(lambda df: df.rename(columns={'abstract': 'text'}))
    >> pt.IterDictIndexer(pt_index_path, blocks=True, fields=['text'])
)
```
Tip📝 - remember to install [pyterrier_doc2query](https://github.com/terrierteam/pyterrier_doc2query) first before you import it

## IV - Pipeline & Evaluation
So, we tried some retrieved methods.
1. BM25
`pt.BatchRetrieve(index, wmodel="BM25")`
Retrieve relevant documents with BM25

2. SDM (Sequential Dependence Model)
`pt.rewrite.SDM()`
SDM creates N-gram representations and their weighting if the input query contains more than one words.

3. Bo1QueryExpansion
`pt.rewrite.Bo1QueryExpansion(index)`
This takes in a set of retrieved documents and generates most relevant tokens and append these tokens back to query. The output is the new query.

We made three pipelines. We had BM25 as our baseline. Since we wanted to try how N-gram representations would impact the retrieved results and how query expansion performs, we generated the following pipelines.
- BM25 **baseline**
- SDM -> BM25
- BM25 -> Bo1QueryExpansion -> BM25

Then, how do we evaluate our pipelines? 🤔  Remember, we want to know how models perform and how many relevant courses are recommend to students.

So, we needed nDCG@10, nDCG@5, P@10, P@5, R@10, R@5 (P=Precision, R=Recall). The reason we have evaluation values @5 and @10 is that we want to know how fast the evaluation values change and how likely highly relevant courses are retrieved.

Here are some codes that we used to evaluate our pipelines.
```
bm25 = pt.BatchRetrieve(index, wmodel="BM25")
sdm = pt.rewrite.SDM()
qe = pt.rewrite.Bo1QueryExpansion(index)

pipeline_1 = sdm >> bm25
pipeline_2 = bm25 >> qe >> bm25

from pyterrier.measures import *
pt.Experiment(
    [bm25, pipeline_1, pipeline_2],
    df_query,
    df_anno[['qid', 'docno','label']],
    eval_metrics=[MAP, nDCG@10, nDCG@5, R@10, R@5, P@10, P@5],
    names=["BM25", "SDM", "QE"]
)
```

### Evaluation Results
Here is a table of how the pipelines using our first indexing perform. You can notice that pipeline with query expansion performed the best.

name |	AP	| nDCG@10	| nDCG@5 |	R@10	| R@5	| P@10	| P@5
--- | --- | --- | --- | --- | --- | --- | --- 
BM25	|0.210000|	0.707263|	0.753723|	0.067500|	0.037917|	0.81|	0.91
SDM|	0.213333|	0.712436|	0.757567|	0.067500|	0.037917|	0.81|	0.91
QE|	0.634167|	0.761060|	0.774291|	0.079167|	0.039583|	0.95|	0.95

