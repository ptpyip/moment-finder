import React, { useState, useEffect } from "react";
import ReactPlayer from 'react-player'

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
          result.videos.map(video => {
            return (
              <div className="video-container container">
                <div className="description-container container">
                  <div className="video-description">
                    {video.name}
                  </div>
                </div>
                <div className="player-container container">
                  <div className="player-wrapper">
                    {/* Use the react player component */}
                    <ReactPlayer url={video.url} width='100%' height='100%' />
                  </div>
                </div>
                <div className="horizontal-scroll-container container">
                  {
                    video.scenes.map(scene => {
                      return (
                        <div className="scene-container container">
                          <div className="scene-description-container container">
                            {scene.timestamp}
                          </div>
                          <div className="thumbnail-container container">
                            <div className="image-container container">
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
