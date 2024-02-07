def group_frame2moments(feature_result):
    """
    here assume feaure are vectorized from one frame.
    given a list of feature result:
    [
        (<dis>, <vector>, <moment_id>), or (<score>, <vector>, <frame_base64>, <moment_id>) 
        ...
    ]
    
    return moment_ids + simlarity_score (sorted):
    [(<moment_id>, <sim_score>), ...]
    """
    ## group by moment_id
    