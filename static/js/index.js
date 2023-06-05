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
        comments: []

    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

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
                if (app.vue.results[i].open === "False") {
                    app.vue.results[i].success_enroll = false;
                }
                else if (app.vue.results[i].num_students < app.vue.results[i].max_num_students) {
                    app.vue.results[i].success_enroll = true;
                }
                else {
                    app.vue.results[i].success_enroll = false;
                }
            }

            // after we find the search results, set the show_search_results_page = true
            app.vue.show_search_results_page = true;
        });        
    }


    app.load_page = function() {
        axios.get(get_session_list_url)
            .then(function(response) {
                app.vue.session_list = response.data.session_list;
                app.vue.session_list = app.enumerate(app.vue.session_list);

                for (let i = 0; i < app.vue.session_list.length; i++) {
                    // if session is created by user who is logged in
                    if (app.vue.session_list[i]["owner"] === response.data.owner) {
                        app.vue.session_list[i].add_edit_status = true;
                        app.vue.session_list[i].remove_delete_status = true;
                    }
                    else {
                        app.vue.session_list[i].add_edit_status = false;
                        app.vue.session_list[i].remove_delete_status = false;

                    }
                    
                }
            });        
    }

    app.enroll_session = function(session_id) {
        axios.post(enroll_session_url,
        {
            // get session id 
            session_id: session_id

        }).then(function(response) {
            app.vue.results = response.data.results;
            app.search();
        });
               
    }


    app.get_comments = function(id) {
        axios.get(get_comments_url, {params: {id: id}})
            .then(function(result) {
                comments_list = result.data.comments;
                for (let i = 0; i < comments_list.length; i++) {
                    let timestamp = comments_list[i]["timestamp"];
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
        disable_comments: app.disable_comments

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
        app.load_page();
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
