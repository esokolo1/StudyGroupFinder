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
  };

  app.methods = {


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
    app.vue.search_sessions();
    axios.get(get_enrolled_schools_url,
    ).then((r) => {
      app.vue.enrolled_schools = r.data.r;
      app.vue.selected_school = app.vue.enrolled_schools[0].id;
    });
  };

  app.init();
};

init(app);
