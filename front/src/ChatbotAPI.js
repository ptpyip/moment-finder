import base64_data from './o_o.jpeg'

const API = {
  GetChatbotResponse: async message => {
    return new Promise(function(resolve, reject) {
      if (message === "hi")  message = "Welcome to chatbot!";
      else message = "echo : " + message;
      
      const result = {
        "message": message,
        "videos": [
          // scene 1
          {
            "name": "Video 1",
            "url": "https://www.youtube.com/watch?v=CT4N_v0dcbc",
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
          // scene 2
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

      resolve(result);
      // setTimeout(function() {
      //   if (message === "hi") resolve("Welcome to chatbot!");
      //   else resolve("echo : " + message);
      // }, 2000);
    });
  }
};

export default API;
