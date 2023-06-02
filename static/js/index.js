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
        results: [],
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
        axios.get(search_url, {params: {school: app.vue.query}})
        .then(function(result) {
            // Console log display what user typed in search bar
            console.log('hello', app.vue.query);

            app.vue.results = result.data.results;
            app.vue.results = app.enumerate(app.vue.results);
            console.log('results', app.vue.results);

            // after we find the search results, set the show_search_results_page = true
            app.vue.show_search_results_page = true;
        });        
    }


    app.load_page = function() {
        axios.get(get_session_list_url)
            .then(function(response) {
                app.vue.session_list = response.data.session_list;
                console.log(app.vue.session_list)
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
        // console.log('abc', session_id);
        axios.post(enroll_session_url,
            {
                // get session id 
                session_id: session_id

            }).then(function(response) {
                app.vue.results = response.data.results;
                app.search();
            });

    }


    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        load_page: app.load_page,
        enroll_session: app.enroll_session,
        search: app.search,
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
