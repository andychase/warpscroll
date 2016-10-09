$(function () {
    $('.datepicker').datepicker();
});

var Trip = Backbone.Model.extend({
    defaults: function () {
        return {
            destination: "",
            start_date: "",
            end_date: "",
            comment: ""
        };
    }
});

var TripCollection = Backbone.Collection.extend({
    url: '/api/user_trips',
    model: Trip,
    comparator: function (m) {
        return m.start_date
    }
});

var trips = new TripCollection();

var TripView = Backbone.View.extend({
    tagName: "div",
    template: _.template($('#trip-card-template').html()),
    initialize: function () {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
    },
    render: function () {
        this.$el.html(this.template(this.model.toJSON()));
        return this;
    },
    clear: function () {
        this.model.destroy();
    }
});

var AppView = Backbone.View.extend({
    el: $("#trip-list"),
    initialize: function () {
        this.$el.html("");
        this.listenTo(trips, 'add', this.addOne);
        this.listenTo(trips, 'reset', this.addAll);
        this.listenTo(trips, 'all', this.render);
        trips.fetch();
    },
    addOne: function (trip) {
        var view = new TripView({model: trip});
        this.$el.append(view.render().el);
    },
    addAll: function () {
        trips.each(this.addOne, this);
    }
});

$(function () {
    var app = new AppView();
});