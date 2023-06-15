let app = {};

let init = (app) => {

  let week_days = [
    'Sunday', 'Monday','Tuesday','Wednesday',
    'Thursday','Friday','Saturday',
  ];
  app.data = {
    session_results:[],
    week_days:week_days,
    enrolled_schools:[],
    filters_on:false,
    search_query:'',
    selected_school:null,
    selected_courses:[],
    open_only:true,
    ta_only:false,
    location_query:'',
    start_after:null,
    start_before:null,
    selected_days:[],
    enrolled_sessions: [], // Initialize sessions as an empty array.
  };
  app.enumerate = (a) => {
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

  app.getSessions = () => {
    axios.get(get_enrolled_sessions_url).then((result) => {
//        console.log("Lets check the data: " + result.data);
//        console.log("Lets stringify it" + JSON.stringify(result.data.r));
//
        app.vue.enrolled_sessions = app.enumerate(result.data.r); // Set the sessions data in Vue
      })
      .catch((error) => {
        console.log(error + " falling into catch");
      });
  };



  app.methods = {
    getSessions: app.getSessions,

    removeSession: function (sessionID) {
      axios
        .post(remove_session_url, {session_id: sessionID})
        .then(() => {
          // Remove the session from the enrolled_sessions array
          app.vue.enrolled_sessions = app.vue.enrolled_sessions.filter(
            (session) => session.id !== sessionID
          );
        })
        .catch((error) => {
          console.log(error);
        });
    },

    enrollSession: function (sessionID) {
      axios
        .post(enroll_session_url, { session_id: sessionID })
        .then((response) => {
          if (response.data.enrolled) {
            // Session enrollment successful, update the enrolled_sessions array
            const enrolledSession = app.vue.sessions.find(
              (session) => session.id === sessionID);
              if (enrolledSession) {
                  enrolledSession.is_enrolled = true;
               }
          }else {
            // Session enrollment failed
            console.log('Failed to enroll in session');
            }
        })
        .catch((error) => {
          console.log(error);
        });
    },

    getEnrollmentStatus: function(sessionId) {
      // Find the session in the 'sessions' array using the session ID
      const session = this.enrolled_sessions.find((session) => session.id === sessionId);

      // Return the enrollment status if the session is found
      if (session) {
        return true;
      }

      // Return a default value if the session is not found
      return false; // or any other default value
    },
    toggle_enroll: function(session){
        if (this.getEnrollmentStatus(session.id)) {
//            console.log("is enrolled so need to unenroll");
            this.removeSession(session.id)
                .then(() => {
            // Update the session's enrollment status
            session.is_enrolled = false;

            // Refresh the sessions data
            this.getSessions();
          })
          .catch((error) => {
            console.log(error);
          });

        }else{
//            console.log("is unenrolled so need to enroll");
            this.enrollSession(session.id)
                .then(() => {
                    // Update the session's enrollment status
                    session.is_enrolled = true;

                    // Refresh the sessions data
                    this.getSessions();
                })
              .catch((error) => {
                console.log(error);
              });

        }
    },


    toggle_filter:function() {
      this.filters_on=!this.filters_on;
    },
    clear_start_after:function() {
      this.start_after = NaN;
    },
    clear_start_before:function() {
      this.start_before = NaN;
    },
    convert_time:function(date,time) {
      return Sugar.Date(time).toLocaleString()
    },
    convert_days:function(n) {
      switch(n) {
        case 127: return ['everyday'];
        case 65: return ['weekends'];
        case 62: return ['weekdays'];
        default: break;
      }
      days_list = [];
      for(let i = 0; i < 7; i++) {
        if (n % 2) {
          days_list.push(week_days[i].slice(0,3));
        }
        n = Math.floor(n / 2);
      }
      return days_list;
    },
    search_sessions:function() {
      let courses = []
      for (const course in this.selected_courses) {
        courses.push(course.id);
      }
      if (!this.filters_on) {
        request_data = {
          search_query:this.search_query,
          school:this.selected_school,
          courses:[],
          open:true,
          ta:false,
          loc:'',
          after:null,
          before:null,
          days:[],
        }
      } else {
        request_data = {
          search_query:this.search_query,
          school:this.selected_school,
          courses:this.selected_courses,
          open:this.open_only,
          ta:this.ta_only,
          loc:this.location_query,
          after:this.start_after,
          before:this.start_before,
          days:this.selected_days,
        }
      }
      axios.post(search_sessions_url,
        request_data
      ).then((r) => {
        this.session_results = r.data.session_results;
      });
    },
  };

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,

  });

  app.init = () => {
    app.getSessions();
    app.vue.search_sessions();
    axios.get(get_enrolled_schools_url,
    ).then((r) => {
      app.vue.enrolled_schools = r.data.r;
      app.vue.selected_school = 0;
    });
  };

  app.init();
};

init(app);
