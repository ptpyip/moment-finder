import React, { useState, useEffect, useRef } from "react";
import ReactPlayer from 'react-player'

const url_matcher = /^http.*$/;

export default function BotMessage({ fetchMessage: fetchResult }) {
  const [isLoading, setLoading] = useState(true);
  const result_p = {
    "message": "...",
    "videos": [
      // scene 1
      {
        "name": "Video 1",
        "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
        "scenes" : [{
          "timestamp": 0,
          "thumbnail": ""
        }]
      },
      // scene 2
      {
        "name": "Video 2",
        "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
        "scenes" : [{
          "timestamp": 0,
          "thumbnail": ""
        }]
      }
    ]
  }
  const [result, setResult] = useState(result_p);

  // reference to the content container for reference to the video player
  const video_refs = useRef(result.videos.map(()=>React.createRef()));

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
          {isLoading ? "..." : result.message}
        {/* </div> */}

      </div>

      {/* The scenes */}
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
                  <ReactPlayer url={video.url} width='100%' height='100%' ref={video_refs.current[video_index]} />
                </div>
                <div className="horizontal-scroll-container container">
                  {
                    video.scenes.map((scene,scene_index) => {
                      return (
                        <div className="scene-container container">
                          <div className="scene-description-container container">
                            Go to timestamp {scene.timestamp}
                          </div>
                          <div className="thumbnail-container container" onClick={()=> {
                            // TODO: get the reference of the react player of the current video
                            // reference to the video container
                            // const video = theContent.current.children[video_index];

                            // reference to ReactPlayer in player-container
                            const player_ref = video_refs.current[video_index];
                            console.log("video_index:"+video_index);
                            const player = player_ref.current;
                            // console.log((player))

                            player.seekTo(scene.timestamp,'seconds');
                            // player.playing = true;
                          }}>
                            <div className="image-container container">
                              {/* scene.thumbnail == "data:image/png;base64, {base64_string}" */}
                              <img src={scene.thumbnail} alt="" />
                            </div>
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
    </div>
  );
}
