def group_frame2moments(feature_result):
    """
    NO NEED
    just use SQL GROUP BY
    '''
        SELECT moment_id, COUNT(*) AS number_of_frame, max(vector <-> '{input_vector.tolist()}') AS distance
        FROM moment_feature_test
        group by moment_id 
        ORDER BY distance LIMIT {int(k)};
    '''
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
    