// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let app = {};

let init = (app) => {
  let week_days = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  // This is the Vue data.
  app.data = {
    week_days: week_days,
    enrolled_sessions: [], // Initialize sessions as an empty array.
  };

  app.enumerate = (a) => {
    let k = 0;
    a.map((e) => {
      e._idx = k++;
    });
    return a;
  };

  // Make an API request to fetch the sessions data.
  app.getSessions = () => {
    axios
      .get(get_enrolled_sessions_url)
      .then((result) => {
        //        console.log("Lets check the data: " + result.data);
        //        console.log("Lets stringify it" + JSON.stringify(result.data.r));
        //
        //        console.log("Lets check result: " + result.data.enrolled_sessions);
        app.vue.enrolled_sessions = app.enumerate(result.data.r); // Set the sessions data in Vue
      })
      .catch((error) => {
        console.log(error + " falling into catch");
      });
  };

  app.removeSession = (sessionID) => {
    axios
      .post(remove_session_url, { session_id: sessionID })
      .then(() => {
        // Remove the session from the enrolled_sessions array
        app.vue.enrolled_sessions = app.vue.enrolled_sessions.filter(
          (session) => session.id !== sessionID
        );
      })
      .catch((error) => {
        console.log(error);
      });
  };

  app.methods = {
    getSessions: app.getSessions,
    removeSession: app.removeSession,
    convert_days: function (n) {
      switch (n) {
        case 127:
          return ["everyday"];
        case 65:
          return ["weekends"];
        case 62:
          return ["weekdays"];
        default:
          break;
      }
      days_list = [];
      for (let i = 0; i < 7; i++) {
        if (n % 2) {
          days_list.push(week_days[i].slice(0, 3));
        }
        n = Math.floor(n / 2);
      }
      return days_list;
    },
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
