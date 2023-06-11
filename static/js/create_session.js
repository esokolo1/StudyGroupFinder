let app = {};

let init = (app) => {

    let date = new Date();
    let YYYY = date.getFullYear();
    let MM = date.getMonth();
    let DD = date.getDate();
    let day = date.getDay();
    let hh = date.getHours();
    let mm = date.getMinutes();
    let week_days = [
      'Sunday', 'Monday','Tuesday','Wednesday',
      'Thursday','Friday','Saturday',
    ];
    let fmt2d = (d) => {
      return ('00'+d).slice(-2);
    }
    let convert_days = (days_list) => {
      let n = 0;
      for (let i = 0; i<week_days.length; i++) {
        n += days_list.includes(week_days[i]) ? Math.pow(2,i) : 0;
      }
      return n;
    }

    app.data = {
      enrolled_courses:[],
      week_days:week_days,
      name:'',
      course:null,
      desc:'',
      ta:false,
      loc:'',
      has_cap:false,
      cap:null,
      is_repeating:false,
      days:[week_days[day]],
      start_time:fmt2d(hh)+':'+fmt2d(mm),
      end_time:fmt2d((hh+1)%24)+':'+fmt2d(mm),
      start_date:YYYY+'-'+fmt2d(MM)+'-'+fmt2d(DD),
      end_date:null,
    };

    app.computed = {
      duration:function() {
        start_hh = Number(this.start_time.slice(0,2));
        start_mm = Number(this.start_time.slice(3));
        end_hh = Number(this.end_time.slice(0,2));
        end_mm = Number(this.end_time.slice(3));
        start_min = start_hh*60 + start_mm;
        end_min = end_hh*60 + end_mm + 24*60;
        mm = (end_min - start_min) % (24*60);
        return mm;
      },
      is_valid_date:function() {
        return (
          this.end_date === null ||
          this.start_date <= this.end_date
        );
      },
      is_valid_form:function() {
        return (
          this.is_valid_date &&
          this.name.length > 0 &&
          this.loc.length > 0
        );
      },
    };

    app.methods = {
      reset_cap:function() {
        this.cap = null;
      },
      set_cap:function() {
        this.cap = this.cap ? this.cap : NaN;
      },
      toggle_end_date:function() {
        this.end_date = this.end_date ? null : this.start_date;
      },
      submit_form:function() {
        if (!this.is_repeating) {
          this.end_date = this.start_date;
          this.days = [week_days[day]];
        }
        this.cap = this.cap ? this.cap : null;
        axios.post(create_new_session_url,
          {
            name:this.name,
            desc:this.desc,
            course:this.course,
            ta:this.ta,
            loc:this.loc,
            cap:this.cap,
            time:this.start_time,
            len:this.duration,
            days:convert_days(this.days),
            start:this.start_date,
            end:this.end_date,
          }
        ).then((r) => {
          window.location=r.data;
        });
      },
    };

    app.init = () => {
      axios.get(get_enrolled_courses_url,
      ).then((r) => {
        app.vue.enrolled_courses = r.data.r;
      });
    };

    app.vue = new Vue({
      el: "#vue-target",
      data: app.data,
      computed: app.computed,
      methods: app.methods,
    });

    app.init();

};

init(app);
