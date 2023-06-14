// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let app = {};

let init = (app) => {
  // This is the Vue data.
  app.data = {
    enrolled_sessions: [], // Initialize sessions as an empty array.
  };

 app.enumerate = (a) => {
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


  // Make an API request to fetch the sessions data.
  app.getSessions = () => {
    axios.get(get_enrolled_sessions_url) // Use the correct URL for fetching sessions
      .then((result) => {
        console.log("Lets check result: " + result.data.enrolled_sessions);
        app.vue.enrolled_sessions = app.enumerate(result.data.enrolled_sessions); // Set the sessions data in Vue
      })
      .catch((error) => {
        console.log(error + " falling into catch");
      });
  };
  app.methods = {
        getSessions: app.getSessions,

  };
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,
  });

  app.init = () => {
        app.getSessions();
  };

  app.init();


};


init(app);
