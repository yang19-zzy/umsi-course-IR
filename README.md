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
si_106 | <course title> <course description>
... | ...
  
2. Query dataframe
qid | query
--- | ---
1 | R programming
... | ...
