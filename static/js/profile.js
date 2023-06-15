let init_profile = (app) => {
  app.data = {
    email: '',
    first: '',
    last: '',
    desc: '',
    editing: false,
    enrolled_schools: [],
    enrolled_courses: [],
  };
  app.computed = {
    invalid_name: function() {
      if ( this.first.length < 1
        && this.last.length < 1 ) {
        return 'a name is required';
      }
    },
    invalid_schools: function() {
      if (this.enrolled_schools.length < 1) {
        return 'choose at least 1 school';
      }
    },
    invalid_courses: function() {
      if (this.enrolled_courses.length < 1) {
        return 'choose at least 1 course';
      }
    },
    invalid_form: function() {
      if ( this.invalid_name
        || this.invalid_schools
        || this.invalid_courses ) {
        return true;
      }
    }
  }
  app.methods = {
    fetch_profile: function() {
      axios.get(fetch_profile_url,
      ).then((r) => {
        this.email=r.data.email;
        this.first=r.data.first;
        this.last=r.data.last;
        this.desc=r.data.desc;
      });
    },
    write_profile: function() {
      axios.post(write_profile_url,{
        first: this.first,
        last: this.last,
        desc: this.desc,
      }).then(() => {
        //this.fetch_profile();
      });
    },
    toggle_editing: function() {
      if (this.editing) this.write_profile();
      this.editing = !this.editing;
    },

    /*search-choose for school*/
    get_enrolled_schools: function() {
      axios.get(fetch_schools_url, { params: {
        my:true,
      }}).then((r) => {
        this.enrolled_schools = r.data.schools;
      });
    },
    click_school: function(school) {
      school.enrolled = !school.enrolled;
      axios.get(enroll_school_url, { params: {
        id: school.id,
        enroll: school.enrolled ? 1 : null,
      }}).then(() => {
        this.get_enrolled_schools();
      });
    },
    display_school: (school) => {
      return school.name;
    },

    /*search-choose for courses*/
    get_enrolled_courses: function() {
      axios.get(fetch_courses_url, { params: {
        my:true,
      }}).then((r) => {
        this.enrolled_courses = r.data.courses;
      });
    },
    click_course: function(course) {
      course.enrolled = !course.enrolled;
      axios.get(enroll_course_url, { params: {
        id: course.id,
        enroll: course.enrolled ? 1 : null,
      }}).then(() => {
        this.get_enrolled_courses();
      });
    },
    display_course: (course) => (
      course.subject + ' ' + course.num + ' - ' + course.title
    ),
  };
  app.vue = new Vue({
    el: '#profile-app',
    data: app.data,
    computed: app.computed,
    methods: app.methods,
  });
  /*init*/
  app.vue.get_enrolled_schools();
  app.vue.get_enrolled_courses();
  app.vue.fetch_profile();
};
let profile_app = {};
init_profile(profile_app);
