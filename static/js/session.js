let init_session = (app) => {
  let d = new Date();
  let week = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday',
  ];
  let date = d.toISOString().slice(0, 10);
  let time_now = d.toTimeString().slice(0, 5);
  app.data = {
    d: d,
    editing: !session_id && editable,
    enrolled_courses: [],
    repeating: false,
    id: session_id,
    author: '',
    course: null,
    name: '',
    desc: '',
    loc: '',
    days: [week[d.getDay()]],
    time_start: time_now,
    time_end: null,
    start: date,
    cap: null,
    ta: false,
    end: date,
    attending: false,
  };
  app.computed = {
    invalid_name: function() {
      if (this.name.length < 1) {
        return 'session name is required';
      }
    },
    invalid_loc: function() {
      if (this.loc.length < 1) {
        return 'a meeting location / link is required';
      }
    },
    invalid_time: function() {
      if (!this.time_start) {
        return 'a start time is required';
      }
    },
    invalid_dates: function() {
      if (!this.start) {
        return 'a start date is required';
      }
      if (!this.repeating) return;
      if (this.end && this.end < this.start) {
        return 'start date cannot be after end date';
      }
    },
    invalid_days: function() {
      if (this.days.length < 1) {
        return 'choose at least 1 meeting day';
      }
    },
    invalid_form: function() {
      if ( this.invalid_name
        || this.invalid_loc
        || this.invalid_time
        || this.invalid_dates ) {
        return true;
      };
    },
    time_len: function() {
      if (!this.time_start || !this.time_end) return null;
      let t1 = this.time_to_min(this.time_start);
      let t2 = this.time_to_min(this.time_end);
      return (t2 + 60*24 - t1) % (60*24);
    },
    start_day: function() {
      if (!this.start) return null;
      let ymd = this.start.match(/\d+/g).map((x) => Number(x));
      this.d.setFullYear(ymd[0]);
      this.d.setMonth(ymd[1]-1);
      this.d.setDate(ymd[2]);
      return week[this.d.getDay()];
    },
  };
  app.methods = {
    toggle_editing: function() {
      if (this.editing) this.write_session();
      this.editing = editable && !this.editing;
    },
    display_course: (course) => (
      course.subject + ' ' + course.num + ' - ' + course.title
    ),
    toggle_end: function() {
      this.end = this.end ? null : this.start;
    },
    time_to_min: (t) => (
      t && t.slice(0, 5)
        .match(/\d+/g)
        .map((x) => Number(x))
        .reduce((a, x) => 60 * a + x)
    ),
    write_session: function() {
      axios.post(write_session_url, {
        id: this.id || null,
        course_id: this.course ? this.course.id : null,
        name: this.name,
        desc: this.desc,
        loc: this.loc,
        days: this.repeating ? this.days : [this.start_day],
        time: this.time_start,
        length: this.time_len,
        start: this.start,
        end: this.repeating ? this.end : this.start,
        cap: this.cap,
        ta: this.ta || null,
      }).then((r) => {
        if (!session_id) window.location = r.data.url;
      });
    },
    delete_session: function() {
      axios.post(write_session_url, {
        id: this.id || null,
        del: true,
      }).then((r) => {
        // redirect
        window.location = r.data.url;
      });
    },
    attend_session: function() {
      this.attending = !this.attending;
      axios.get(attend_session_url, { params: {
        id: this.id,
        attend: this.attending ? true : null,
      }});
    },
    get_session: function() {
      axios.get(fetch_sessions_url, { params: {
        id: this.id,
      }}).then((r) => {
        for (const i in r.data.session) {
          if (i in app.data) {
            this[i] = r.data.session[i];
          }
        }
        this.repeating = (this.start != this.end);
        this.time_start = r.data.session.time.slice(0, 5);
        let len = r.data.session.len;
        if (len) {
          this.d.setMinutes(len);
          this.time_end = this.d.toTimeString().slice(0, 5);
        }
      });
    },
  };
  app.vue = new Vue({
    el: '#session-app',
    data: app.data,
    computed: app.computed,
    methods: app.methods,
  });
  /*init*/
  axios.get(fetch_courses_url, { params: {
    my: true,
  }}).then((r) => {
    app.vue.enrolled_courses = r.data.courses;
  });
  if (session_id) app.vue.get_session();
};
let session_app = {};
init_session(session_app);
