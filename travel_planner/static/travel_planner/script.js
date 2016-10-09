// https://docs.djangoproject.com/en/1.10/ref/csrf/
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
function get_date_only(date) {
    if (!date)
        return null;
    var split_date = date.split("-");
    var year = parseInt(split_date[0]);
    var month = parseInt(split_date[1]);
    var day = parseInt(split_date[2]);
    return new Date(year, month - 1, day);
}
function dateToDateString(d) {
    return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
}

var Trip = Backbone.Model.extend({
    url: function () {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    },
    defaults: function () {
        var today = dateToDateString(new Date());
        return {
            destination: "",
            start_date: today,
            end_date: today,
            days_left: "",
            comment: ""
        };
    }
});

var TripCollection = Backbone.Collection.extend({
    url: '/api/user_trips/',
    model: Trip,
    comparator: function (m) {
        return -get_date_only(m.get("start_date"));
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
    events: {
        'click .remove-dest': function (e) {
            this.model.destroy();
            e.preventDefault();
        },
        'keypress input[name=destination]': function (e) {
            if (e.keyCode == 13) e.target.blur();
        },
        'blur input[name=destination],textarea': 'edit',
        'hide .datepicker': 'date_edit'
    },
    date_edit: function (e) {
        this.edit(e);
        trips.sort();
    },
    edit: function (e) {
        var save_value = {};
        save_value[e.target.name] = e.target.value;
        if ((e.target.name == "start_date" || e.target.name == "end_date") && !e.target.value.trim())
            save_value[e.target.name] = null;
        this.model.save(save_value);
    },
    render: function () {
        this.$el.html(this.template(this.model.toJSON()));
        this.$el.find(".datepicker").datepicker();
        return this;
    }
});

var AppView = Backbone.View.extend({
    el: $("#trip-list"),
    initialize: function () {
        this.current = this.$el.children(".current-trips");
        this.upcoming = this.$el.children(".upcoming-trips");
        this.past = this.$el.children(".past-trips");

        this.listenTo(trips, 'add', this.addOne);
        this.listenTo(trips, 'reset', this.addAll);
        this.listenTo(trips, 'sort', this.addAll);
        this.listenTo(trips, 'all', this.render);
        trips.fetch();
    },
    sortIntoStacks: function (trip, view) {
        var today = get_date_only(dateToDateString(new Date()));
        var start_date = get_date_only(trip.get("start_date"));
        var end_date = get_date_only(trip.get("end_date"));
        if (!start_date || !end_date || (start_date <= today && end_date >= today))
            this.current.prepend(view.render().el);
        else if (start_date <= end_date && end_date < today)
            this.past.prepend(view.render().el);
        else
            this.upcoming.prepend(view.render().el);
    },
    addOne: function (trip) {
        var view = new TripView({model: trip});
        this.sortIntoStacks(trip, view);
    },
    addAll: function () {
        this.$el.children(".trip-section").html("");
        trips.each(this.addOne, this);
    }
});

$(function () {
    var app = new AppView();
    $(".add-dest").click(function (e) {
        trips.create();
        e.preventDefault();
    });
});