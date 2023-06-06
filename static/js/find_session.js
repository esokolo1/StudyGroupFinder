// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {
  // This is the Vue data.
  app.data = {
    // Complete as you see fit.
    session_list: [],
    school: "All",
    term: "All",
    status: "All",
    class_name: "",
    location: "",
    meeting_days: [],
    meeting_time_from: "",
    meeting_time_to: "",
    ta_tutor: "All",
  };

  app.enumerate = (a) => {
    // This adds an _idx field to each element of the array.
    let k = 0;
    a.map((e) => {
      e._idx = k++;
    });
    return a;
  };

  app.search = function () {
    axios
      .post(get_search_results_url, {
        school: app.vue.school,
        term: app.vue.term,
        status: app.vue.status,
        class_name: app.vue.class_name,
        location: app.vue.location,
        meeting_days: app.vue.meeting_days,
        meeting_time_from: app.vue.meeting_time_from,
        meeting_time_to: app.vue.meeting_time_to,
        ta_tutor: app.vue.ta_tutor,
      })
      .then((r) => {
        console.log(r.data.session_list);
        app.vue.session_list = r.data.session_list;
      });
  };

  app.load_page = function () {};

  // This contains all the methods.
  app.methods = {
    // Complete as you see fit.
    load_page: app.load_page,
    search: app.search,
  };

  // This creates the Vue instance.
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,
  });

  // And this initializes it.
  app.init = () => {
    // Put here any initialization code.
    // Typically this is a server GET call to load the data.
    app.load_page();
  };

  // Call to the initializer.
  app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
