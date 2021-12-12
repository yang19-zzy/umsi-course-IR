# from pandas.core.dtypes import base


def get_documents_dict():
    import os
    umsi_doc_list = os.listdir('Data/UMSI')
    documents = {}
    for filename in umsi_doc_list:
        with open(f"Data/UMSI/{filename}", "r") as f:
            documents[filename.split('.')[0]] = f.read().split('\n')[0]
    return documents


def get_course_link(base_url='https://www.si.umich.edu/programs/courses', course_num=""):
    return f"{base_url}/{course_num.split('_')[1]}"


def get_top_5_related(query):

    import pyterrier as pt
    if not pt.started():
        pt.init() 

    # load index
    index = pt.IndexFactory.of('./index/iterdictindex/data.properties')
    index_wiki = pt.IndexFactory.of('./index/wikir_en1k/data.properties')

    # pipeline
    bm25 = pt.BatchRetrieve(index, wmodel="BM25")
    bm25_wiki = pt.BatchRetrieve(index_wiki, wmodel="BM25")
    qe_wiki = pt.rewrite.Bo1QueryExpansion(index_wiki)

    pipeline = bm25_wiki >> qe_wiki >> bm25

    # return results

    transform = pipeline.transform(query)
    results = transform['docno'].tolist()[:5]
    return results
