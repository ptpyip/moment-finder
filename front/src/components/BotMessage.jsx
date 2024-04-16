import React, { useState, useEffect, useRef } from "react";
import ReactPlayer from 'react-player'

const url_matcher = /^http.*$/;

const sanitizeHTML = (str) => {
  return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};

export default function BotMessage({ fetchMessage: fetchResult, query }) {
  query = query != undefined ? sanitizeHTML(query) : "";

  const [isLoading, setLoading] = useState(true);
  const result_p = {
    "message": "...",
    "videos": [
      // // scene 1
      // {
      //   "name": "Video 1",
      //   "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
      //   "scenes" : [{
      //     "timestamp": 0,
      //     "thumbnail": ""
      //   }]
      // },
      // scene 2
      // {
      //   "name": "Video 2",
      //   "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
      //   "scenes" : [{
      //     "timestamp": 0,
      //     "thumbnail": ""
      //   }]
      // }
    ]
  }
  let video_refs = useRef([])
  const [result, setResult] = useState(result_p);
  if (result != undefined) {
    if (result.videos.length > 0) {
      video_refs.current = result.videos.map(()=>React.createRef());
    }
  }

  // reference to the content container for reference to the video player

  useEffect(() => {
    async function loadMessage() {
      const result = await fetchResult();
      setLoading(false);
      setResult(result);
    }
    loadMessage();
  }, []);
  // console.log("Hello world")
  // console.log(result);
  

  return (
    <div className="bot-message message-container">
      {/* Upper section of the text */}
      <div className="text-container container">
        {/* <div className="bot-message"> */}
          {isLoading ? "Looking for '"+query+"' passionately..." : result.message}
        {/* </div> */}

      </div>

      {/* The scenes */}
      { result.videos.length == 0 ? undefined : (
          <div className="content-container container">
            {
              result.videos.map((video,video_index) => {
                return (
                  <div className="video-container container">
                    <div className="description-container container">
                      <div className="video-description">
                        {video.name}
                      </div>
                    </div>
                    <div className="player-container container">
                      {/* Use the react player component */}
                      <ReactPlayer controls url={video.url} width='100%' height='100%' ref={video_refs.current[video_index]} />
                    </div>
                    <div className="horizontal-scroll-container container">
                      {
                        video.scenes.map((scene,scene_index) => {
                          let time = scene.timestamp
                          return (
                            <div className="scene-container container">
                              <div className="scene-description-container container" onClick={()=> {
                                // TODO: get the reference of the react player of the current video
                                // reference to the video container
                                // const video = theContent.current.children[video_index];

                                // reference to ReactPlayer in player-container
                                // console.log("video_index:"+video_index);
                                // console.log((player))
                                
                                const player_ref = video_refs.current[video_index];
                                const player = player_ref.current;
                                player.seekTo(time,'seconds');
                                // player.playing = true;
                              }}>
                                <button>Go to timestamp {time} - similarity:{scene.sim_score}</button>
                              </div>
                            </div>
                          )
                        })
                        
                      }
                    </div>

                  </div>
                )
              })
            }
          </div>
        )
      }
    </div>
  );
}
