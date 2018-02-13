$(function() {
    // this ensures that the code in this scope does not run
    // until all the html elements and javascript dependencies are loaded.

    // a store is a simplified way to store data using Vue
    store = new Vuex.Store({
        state: {
            data1: [],
        },
        mutations: {
            data1 (state, data) {
                // commits new data to the state
                state.data1 = data1;
            },
        },
        actions: {
            // in case the store needs to do something not commit related
            // generally not used.
            }
        },
    });

    // Vue basic setup to work with Django

    vueApp = new Vue({
        el: "#html_element",
        store: store,
        // Vue uses {{}} normally, but Django needs those, so we change them
        delimiters: ["((","))"],
        // This is data that needs to be 2 way bound (such as the filter input)
        // These cannot be set to undefined/null. 
        data: {
            stuff: [],
            stuff1: {},
            stuff2: false,
            stuff3: "",
        },
        computed: {
            // this is for data that is computed based on changing data or accessing store data
            data1: function() {
                // how we access the store data
                return store.state.data1;
            }
            stuff3_computed: function() {
                // notice that we access data bound to the Vue object using the 'this' keyword
                return this.stuff3 + " automatically adding on something else";
            }
        }
        mounted: function() {
            /* this is run at the beginning of Vue's life cycle.
            // Use this to run stuff that needs to happen immediately
            // once the page loads properly.
            // accessing data from here will be through the 'this' keyword.
            */
        },
        methods: function() {
            method1: function() {
                // notice that how we access data in methods is different from computed
                return vueApp.stuff3;
            }
        }
    })
})

// how to do an ajax request with jQuery and Django

$.post("{% url 'competition:manage' competition=competition.id %}", {
    // data goes here in JSON format
    // this is needed to make sure Django doesn't reject the AJAX request. Don't touch this.
    csrfmiddlewaretoken: "{{csrf_token}}", 
}, function(response, status, xhr) {
    // runs on response.
}).always(function(data) {
    // runs regardless of whether the server responds or not.
})