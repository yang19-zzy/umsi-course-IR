# Improve How Students Search for Courses

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
Here, we
