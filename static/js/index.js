// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        add_edit_status: false,
        remove_delete_status: false,
        session_list: [],


        show_search_results_page: false,
        query: "",
        term: "",
        status: "",
        class_name: "",
        location: "",
        meeting_date: "",
        meeting_start: "",
        meeting_end: "",
        ta: "",
        results: [],

        success_enroll: true,

        comments_displayed: false,
        new_comment: "",
        comments: [],

        // Calendar
        year: "",
        month: "",
        month_name: "",
        date: [],
        weeks1: [],
        upcoming_sessions: [],
        is_clicked: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    // if user clicks right arrow, display next month calendar
    app.nextCal = function(month, year) {
        // if current month is December, next month = 1
        // add year + 1
        if (month === 12) {
            app.vue.month = 1;
            app.vue.year += 1;
        }
        else {
            app.vue.month += 1;
        }
        axios.get(calendar_url, {
            params: {
                month: app.vue.month,
                year: app.vue.year}})
        .then(function(r) {
            app.vue.month = r.data.month;
            app.vue.month_name = r.data.month_name;
            app.vue.year = r.data.year;
            app.vue.weeks1 = r.data.weeks;
            for(var i = 0; i < app.vue.weeks1.length; i++) {
                var week = app.vue.weeks1[i];
                for(var j = 0; j < week.length; j++) {
                    if (app.vue.weeks1[i][j] === 0) {
                        app.vue.weeks1[i][j] = null;
                    }
                }
            }
            app.vue.is_clicked = false;
        });
    }

    // if user clicks left arrow, display prev month calendar
    app.prevCal = function(month, year) {
        // if current month is January, prev month is December
        // subtract year - 1
        if (month === 1) {
            app.vue.month = 12;
            app.vue.year -= 1;
        }
        else {
            app.vue.month -= 1;
        }
        axios.get(calendar_url, {
            params: {
                month: app.vue.month,
                year: app.vue.year}})
        .then(function(r) {
            app.vue.month = r.data.month;
            app.vue.month_name = r.data.month_name;
            app.vue.year = r.data.year;
            app.vue.weeks1 = r.data.weeks;
            for(var i = 0; i < app.vue.weeks1.length; i++) {
                var week = app.vue.weeks1[i];
                for(var j = 0; j < week.length; j++) {
                    if (app.vue.weeks1[i][j] === 0) {
                        app.vue.weeks1[i][j] = null;
                    }
                }
            }
            app.vue.is_clicked = false;
        });
    }

    // Create Calendar
    app.createCalendar = function() {
        axios.get(calendar_url)
        .then(function (r) {
            app.vue.month = r.data.month;
            app.vue.month_name = r.data.month_name;
            app.vue.year = r.data.year;
            app.vue.weeks1 = r.data.weeks;
            for(var i = 0; i < app.vue.weeks1.length; i++) {
                var week = app.vue.weeks1[i];
                for(var j = 0; j < week.length; j++) {
                    if (app.vue.weeks1[i][j] === 0) {
                        app.vue.weeks1[i][j] = null;
                    }
                }
            }
            app.vue.is_clicked = false;
        });
   
    }

    // once user clicks specific date on calendar, schedule card will pop up
    app.getEvents = function(month, cell, year) {
        app.vue.date = []
        app.vue.date.push(cell);
        app.vue.is_clicked = true;
        axios.get(events_url, {
            params: {
                month: app.vue.month,
                date: app.vue.date[0],
                year: app.vue.year}})
            .then(function(response) {
                app.vue.upcoming_sessions= response.data.events_list;
                // sort by starttime
                app.vue.upcoming_sessions.sort((a, b) => (a.session_time > b.session_time) ? 1 : -1)
            });
    }

    // close upcoming schedule events if user clicks "x" button on schedule page
    app.closeEvents = function() {
        app.vue.is_clicked=false;
    }

    // SEARCH FUNCTION
    app.search = function() {
        // sends query to server
        axios.get(search_url, {
            params: {
                school: app.vue.query,
                term: app.vue.term,
                status: app.vue.status,
                class_name: app.vue.class_name,
                location: app.vue.location,
                meeting_date: app.vue.meeting_date,
                meeting_start: app.vue.meeting_start,
                meeting_end: app.vue.meeting_end,
                ta: app.vue.ta,}})
        .then(function(result) {
            app.vue.results = result.data.results;
            app.vue.results = app.enumerate(app.vue.results);
            // check if num_students < max_num_students or open/closed status == "False"
            for (let i = 0; i < app.vue.results.length; i++) {
                // if session is closed, user are not allowed to enroll session
                if (app.vue.results[i].open === "False") {
                    app.vue.results[i].success_enroll = false;
                }
                // if num_students < max_num_students, display "enroll" button on search page
                else if (app.vue.results[i].num_students < app.vue.results[i].max_num_students) {
                    app.vue.results[i].success_enroll = true;
                }
                else { 
                    // if num_students >= max_num students, user are not allowed to enroll session
                    app.vue.results[i].success_enroll = false;
                }
            }
            // after we find the search results, set the show_search_results_page = true
            app.vue.show_search_results_page = true;
        });        
    }

    // create_session results page (edit/delete, remove button)
    app.load_page = function() {
        axios.get(get_session_list_url)
            .then(function(response) {
                app.vue.session_list = response.data.session_list;
                app.vue.session_list = app.enumerate(app.vue.session_list);

                for (let i = 0; i < app.vue.session_list.length; i++) {
                    // if session is created by user who is logged in
                    if (app.vue.session_list[i]["owner"] === response.data.owner) {
                        // display "edit"/"delete" button on create_session_results page
                        app.vue.session_list[i].add_edit_status = true;
                        app.vue.session_list[i].remove_delete_status = true;
                    }
                    else {
                        // else session is created by others
                        // display "remove" button on create_session_results page
                        app.vue.session_list[i].add_edit_status = false;
                        app.vue.session_list[i].remove_delete_status = false;
                    }    
                }
            }); 
            // createCalendar - schedule/dashboard page
            app.createCalendar();
    }

    // enroll_session - user can enroll session in find_session.html
    // after user clicks "enroll", enrolled session will be displayed on create_session_results page
    app.enroll_session = function(session_id) {
        axios.post(enroll_session_url,
        {
            // get session id 
            session_id: session_id

        }).then(function(response) {
            app.vue.results = response.data.results;
            // reload app.search page
            app.search();
        });
               
    }


    app.get_comments = function(id) {
        axios.get(get_comments_url, {params: {id: id}})
            .then(function(result) {
                comments_list = result.data.comments;
                for (let i = 0; i < comments_list.length; i++) {
                    let timestamp = comments_list[i]["comment_timestamp"];
                    comments_list[i]["time"] = Sugar.Date(timestamp + "Z").relative();
                }
                app.vue.comments = comments_list;
                app.vue.comments_displayed = true;
            })
    }

    app.add_comment = function(id) {
        axios.post(add_comment_url, {id: id, new_comment: app.vue.new_comment})
            .then(function(result) {
                app.vue.new_comment = "";
                app.get_comments(id);
            })
    }

    app.disable_comments = function() {
        app.vue.comments_displayed = false;
    }


    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        load_page: app.load_page,
        enroll_session: app.enroll_session,
        search: app.search,
        get_comments: app.get_comments,
        add_comment: app.add_comment,
        disable_comments: app.disable_comments,

        
        createCalendar: app.createCalendar,
        getEvents: app.getEvents,
        closeEvents: app.closeEvents,
        prevCal: app.prevCal,
        nextCal: app.nextCal,
        
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        
        // app.load_page - create_session_results page
        app.load_page(); 
        
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
