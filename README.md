# Improve How Students Search for Courses
(tl;dr)
This project uses Pyterrier to index documents(course descriptions) and retrieve top 10 most relevant courses with Wikipedia collection indexing and its query expansion.


## I - Project Intention
This project is originally a course project from [UMSI 650 - Information Retrieval](https://www.si.umich.edu/programs/courses/650). Based on our own experience as students, we know that students are struggling with choosing the right courses for themselves, especially when they are still unsure about their future career path and want to try anything they're interested in.

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

Then, how do we evaluate our pipelines? 🤔  

So, we needed nDCG@10, nDCG@5, P@10, P@5, R@10, R@5 (P=Precision, R=Recall). The reason we have evaluation values @5 and @10 is that we want to know how evaluation values change. Also, remember, we want to know how models perform and how many relevant courses are recommend to students so that Recall is the one we care more about.

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

Then we tried to use other indexing that we have discussed earlier. And here is the evaluation results. You can notice that when using query expansion with Wikipedia indexing, the model has the best performance.

name |	AP	| nDCG@10	| nDCG@5 |	R@10	| R@5	| P@10	| P@5
--- | --- | --- | --- | --- | --- | --- | --- 
BM25_baseline|	0.471802|	0.707263|	0.753723|	0.162|	0.091|	0.810|	0.91
SDM	|0.475216|	0.711562|	0.769291|	0.161|	0.090|	0.805|	0.90|
QE_doc2query|	0.561712|	0.729719|	0.772821|	0.167|	0.092|	0.835|	0.92
QE_wiki|	0.613924|	0.745158|	0.767340|	0.179|	0.095|	0.895|	0.95


## V - Deployment
In order to make the project outcome as real as possible, we used [streamlit](https://streamlit.io/) to deploy the retrieve model. Since we faced some technical issue, we can only share a screenshot of our "website". 

![Our streamlit app](https://github.com/yang19-zzy/umsi-course-IR/blob/main/image/app.png)

## VI - Discussion
As we discussed in the introduction, the course search system UMSI students currently have is Atlas. The target user of our systems might only know that they want to learn Django but the word Django is often not specified in the course name nor in the course description which makes it difficult for students when deciding which course to take if they have to select a few courses from the whole university. What’s worse, this kind of keyword search is not supported by Atlas, and that is why we are designing our IR system to help students find courses. For example, as shown below in the Atlas screenshot, we can see that there is no result for the query “django”, which indicates that using additional knowledge base to expand the queries is a more appropriate approach for our project. Also, because we didn’t have enough training data, we conducted query expansion according to the pseudo relevance feedback documents retrieved from WikiPedia. 

Increasing recall and achieving search improvement are what we hoped to have: our project objective is to provide students with more course options which they were not aware of before. Therefore, instead of precision, we care more about recall. Moreover, based on our course selection experience, ten retrieved documents for a query is better than five retrieved documents since it is always helpful to know more about what other options are available.
During the experiments, we found something interesting. Hence, we chose to focus on R@10. 

Among all the three indexing methods, query expansion with Wikipedia achieved the highest R@10, which means that the augmented WikiPedia knowledge helped us find more related courses. This result achieved our expectation of augmented knowledge base and this method did improve the search result on our website. 

Also, SDM does not have significant improvement on the scores, which is due to the number of our query terms. SDM will create N-Grams representation and weighting for the query terms; however, most of our queries consist of no more than three terms. This is the reason why there is no big difference between the BM25 baseline and SDM.

Besides, doc2query is not performing as well as we expected which could have been resulted from the pattern of our queries. Our queries are short and they are not like a sentence of questions; therefore, we think this is the reason why the doc2query generated queries are not helping a lot.

## VII - Conclusion
This project aims to provide wider course selection options for students who are not aware of what courses are related to their topics of interest. Since the current course selecting website, Atlas, is not supporting keyword search, we decided to create one information retrieval system that does support this function. The method we used to solve this problem is to add additional knowledge base indexed from Wikipedia dataset obtained through PyTerrier and conduct query expansion using this additional index. This method improved the recall and satisfied our expectations when tested on our website.

## VIII - Next Steps
We realized that full annotation for each query and document will lead to more plausible evaluation scores, so if we had more time we would have annotated all the documents retrieved by BM25. Moreover, we also plan to implement learning-to-rank machine learning models which also need full annotation if we hope to really see some improvements. 
