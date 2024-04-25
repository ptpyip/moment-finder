
# Retrieval 

## single vector

#### frame vector
-   Naive apoarch:
    ``` python
    moment_distances = []   
    for moment_id, frame_vectors in moments:                    # O(N)
        moment_distances.append(
            ## Assome each moment contains  L number of frames.
            ## and vector dimeantion is constant D
            moment_id, min(frame_vectors @ query_vector)        # O(LD)
        )
    moment_ids = sort(distance, axis=1)[: k]                    # ignore
    ```
    $\rightarrow O(NL)$ (const $D << NL$)

-   Vector Indexed Version
    ``` python
    C = 100     # frame candidate num, where C < D
    top_frames = frames.vector_idex.query(query_vector, top=C)      # O(log(NL)D)

    ## Group by moment_id +  ORDER by min(distance)
    moment_distances = []   
    for frame_id, distance, moment_id in top_frames:                # O(C)
        current_distance = moment_distance.get(moment_id, default=1.0)
        if current_distance > distance :
            ### update min distance
            moment_distance[moment_id] = distance

    moment_ids = moment_distances.sort_by_distance[:k]
    ```
    $\rightarrow O(\log(NL))$ (const $D << NL$)

-   SQL Version
    ``` SQL
    SELECT moment_id, min(distance) AS min_distance
    FROM (
        SELECT moment_id,
            vector <=> <query_vector> AS distance       -- using vector index
        FROM frames
        ORDER BY distance limit 100
    ) AS vector_table
    GROUP BY moment_id       
    ORDER BY min(distance) limit 5
    -- Plus Join iwth moments ... 
    ```

#### Moment Vector

-   Naive apoarch:
    ``` python
    moment_distances = []   
    for moment in moments:                                          # O(N)
        moment_distances.append(
            ## Assome vector dimeantion D
            moment.id, moment.vector @ query_vector                 # O(D)
        )
    moment_retrieval = sort(distance, axis=1)[: k]                  # ignore
    ```
    $\rightarrow O(N)$ 

-   Vector Indexed Version
    ``` python
    C = 100     # frame candidate num, where V
    top_moments = moments.vector_idex.query(query_vector, top=k)     # O(log(N)D)
    moment_retrieval = top_moments[:k]
    ```
    $\rightarrow O(\log(N))$ 

-   SQL Version
    ``` SQL
    SELECT id, name, timestamp,
        vector <=> <query_vector> AS distance               -- using vector index
    FROM moments
    ORDER BY distance limit 5
    ```

#### Text Vector ??

## Multi-vector
- Naivie Distance: \
 $dist = \frac{1}{2} ( dist_{moment} + min(dist_{frames}))$

- tuned version: \
 $dist = \alpha \times dist_{moment} + (1-\alpha) \times min(dist_{frames})$
 

-   Naive apoarch:
    ``` python
    moment_distances = []   
    for moment in moments:                    # O(N)
        ## Assome each moment contains  L number of frames.
        ## and vector dimeantion is constant D
        frame_lvl_dist = min(moment.frame_vectors @ query_vector)        # O(LD)
        moment_lvl_dist = moment.vector @ query_vector                  # O(D)
        moment_distances.append(
            moment.id, (aplha*moment_lvl_dist + (1-alpha)*frame_lvl_dist
        )
    moment_ids = sort(distance, axis=1)[: k]                    # ignore
    ```
    $\rightarrow O(NL)$ (const $D << NL$)

