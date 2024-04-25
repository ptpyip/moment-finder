import base64_data from './o_o.jpeg'

const protocol = "http://";
const domain_name = "localhost:8000";
const api_path = "/moments?";
const api_endpoint = protocol + domain_name + api_path;

const video_path = "/stream/";
const video_location = protocol + domain_name + video_path;

const welcome_message = "Tell me what you want, I'll give you what you want :|";

const sanitizeHTML = (str) => {
  return str.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};

const API = {
  GetChatbotResponse: async query => {
    query = sanitizeHTML(query); // sanitize input

    let reply;  // the message for the query

    // this serves only as a template
    let result = {
      "message": reply,
      "videos": [
        // video 1
        {
          "name": "Video 1",
          // "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
          // "url": "http://vml1wk132.cse.ust.hk/stream/vid.mp4",
          "url": "http://localhost:8000/stream/vid.mp4",
          "scenes" : [
            {
              "timestamp": 2,
              "thumbnail": base64_data
            },
            {
              "timestamp": 10,
              "thumbnail": base64_data
            }
          ]
        },
        // video 2
        {
          "name": "Video 2",
          "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
          "scenes" : [{
            "timestamp": 0,
            "thumbnail": base64_data
          }]
        }
      ]
    }
    // default result has no videos, only message
    result.videos = [];

    // Scenario when the program just started, no query yet
    if (query === "hi") result.message = welcome_message;
    else {
      try {
        // here is a query sent to the api endpoint
        let response = await fetch(api_endpoint + new URLSearchParams({
          query: query
        }));
        // try to read the json from the response, its format should look 
        // like the one above
        let data = await response.json();
        if (data.results != undefined) {
          // format of results : array of {
          //     "query": query,
          //     "vid":  vid,      
          //     "timestamp": timestamp,
          //     "sim_score": 1 - cos_dist 
          // }
          let videos = [];
          // sort the scenes according to the scores
          data.results.sort((item1, item2)=>{
            return -(item1.sim_score - item2.sim_score);
          })
          for (let i=0; i<data.results.length; i++) {
            let result = data.results[i];
            const name = "Video "+(i+1);
            const url = video_location +result.vid+".mp4";
            const scenes = [
              {timestamp:[parseInt(result.timestamp[0]),parseInt(result.timestamp[1])],
                sim_score:result.sim_score,
              // thumbnail:base64_data
              }
            ];
            // check if the video was present already
            const exist = videos.find(item => {return item.vid_name == result.vid});
            if (exist == undefined) {
              videos.push({name:name, url:url, scenes:scenes, vid_name:result.vid});
            }
            else {
              // when the same video also has targeted scenes
              exist.scenes.push(
                {timestamp:[parseInt(result.timestamp[0]),parseInt(result.timestamp[1])],
                  sim_score:result.sim_score
                }
              )
            }
          }

          // just turn each sim_score to display at max 4 decimal places
          videos.forEach(video => {
            video.scenes.forEach(scene=> {
              let str = scene.sim_score.toString();
              str = str.length > 6 ? str.substring(0,6) : str;
              scene.sim_score = str;
            })
          })

          result.videos = videos;
          const original_query = data.results.length > 0? data.results[0].query : 'undefined';
          result.message = "Here are "+result.videos.length+" videos with '"+ original_query + "' with total of "+data.results.length+" scenes.";
          // result.message = data.message;
          // result.videos = data.videos;
        }
        else {
          throw {name: "API json response format error", message:"message or videos is undefined"};
        }
      }
      catch (error) {
        // console.log(error);
        // print(error);
        // throw(error);
        result.videos = []
        result.message = "Sorry wasn't listening, I took too long and forget already, please repeat again.. X_X";
      }
    }

    return result
  }
};

export default API;
