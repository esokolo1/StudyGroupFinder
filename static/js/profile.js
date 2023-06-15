let app = {};

let init = (app) => {
  app.data = {
    email: "",
    first_name: "",
    last_name: "",
    description: "",
    selected_schools: [],
    selected_courses: [],
    min_selected_schools: 1,
    min_selected_courses: 1,
    is_saved: false,
  };

  app.computed = {
    is_valid_name: function () {
      return this.first_name.length > 0 || this.last_name.length > 0;
    },
    is_valid_form: function () {
      return (
        this.is_valid_name &&
        this.selected_schools.length >= this.min_selected_schools &&
        this.selected_courses.length >= this.min_selected_courses
      );
    },
  };

  app.methods = {
    save_profile: function () {
      if (this.is_valid_form) {
        this.is_saved = false;
        axios
          .post(save_profile_url, {
            first_name: this.first_name,
            last_name: this.last_name,
            description: this.description,
            enrolled_schools: this.selected_schools,
            enrolled_courses: this.selected_courses,
          })
          .then(() => {
            this.is_saved = true;
          });
      }
    },
  };

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods,
    computed: app.computed,
  });

  app.init = () => {
    axios.get(get_profile_url).then((r) => {
      app.vue.email = r.data.email;
      app.vue.first_name = r.data.first_name;
      app.vue.last_name = r.data.last_name;
      app.vue.description = r.data.description;
    });
    axios.get(get_enrolled_schools_url).then((r) => {
      app.vue.selected_schools = r.data.r;
    });
    axios.get(get_enrolled_courses_url).then((r) => {
      app.vue.selected_courses = r.data.r;
    });
    app.vue.is_saved = true;
  };

  app.init();
};

init(app);
console.log(app.vue);
