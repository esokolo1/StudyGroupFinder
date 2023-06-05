let app = {};

let init = (app) => {

    app.data = {
      school_search_query:'',
      course_search_query:'',
      school_list:[],
      course_list:[],
      email:'',
      first_name:'',
      last_name:'',
      description:'',
      selected_schools:[],
      selected_courses:[],
      is_saved:false,
    };

    app.computed = {
      is_valid_name:function() {
        return (
          this.first_name.length > 0
          || this.last_name.length > 0
        );
      },
      is_valid:function() {
        return (
          this.is_valid_name
          && this.selected_schools.length > 0
          && this.selected_courses.length > 0
        );
      },
    };

    app.methods = {
      save_profile:function() {
        if (!this.is_not_valid) {
          this.is_saved = false;
          axios.post(save_profile_url,
            {
              first_name:this.first_name,
              last_name:this.last_name,
              description:this.description,
              enrolled_schools:this.selected_schools,
              enrolled_courses:this.selected_courses,
            }
          ).then(() => {
            this.is_saved = true;
          });
        }
      },
      search_schools:function() {
        axios.get(
          get_schools_url,
          {params:{query:this.school_search_query}},
        ).then((r) => {
          this.school_list = r.data.school_list;
        });
      },
      search_courses:function() {
        axios.get(
          get_courses_url,
          {params:{query:this.course_search_query}},
        ).then((r) => {
          this.course_list = r.data.course_list;
        });
      },
      toggle_school_select:function(school) {
        for (let i = 0; i<this.selected_schools.length; i++) {
          if (this.selected_schools[i].id==school.id) {
            this.selected_schools.splice(i,1);
            return;
          }
        }
        this.selected_schools.push(school);
      },
      toggle_course_select:function(course) {
        for (let i = 0; i < this.selected_courses.length; i++) {
          if (this.selected_courses[i].id == course.id) {
            this.selected_courses.splice(i,1);
            return;
          }
        }
        this.selected_courses.push(course);
      },
    };

    app.vue = new Vue({
      el: "#vue-target",
      data: app.data,
      methods: app.methods,
      computed: app.computed,
    });

    app.init = () => {
      axios.get(get_profile_url,
      ).then((r) => {
        app.vue.email = r.data.email;
        app.vue.first_name = r.data.first_name;
        app.vue.last_name = r.data.last_name;
        app.vue.description = r.data.description;
      });
      axios.get(get_schools_url,
      ).then((r) => {
        app.vue.school_list = r.data.school_list;
      });
      axios.get(get_courses_url,
      ).then((r) => {
        app.vue.course_list = r.data.course_list;
      });
      axios.get(get_enrolled_schools_url,
      ).then((r) => {
        app.vue.selected_schools = r.data.enrolled_schools;
      });
      axios.get(get_enrolled_courses_url,
      ).then((r) => {
        app.vue.selected_courses = r.data.enrolled_courses;
      });
      app.vue.is_saved = true;
    };

    app.init();
};

init(app);
