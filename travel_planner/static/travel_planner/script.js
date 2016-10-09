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
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(function () {
    $('.datepicker').datepicker();

});

var Trip = Backbone.Model.extend({
     url: function() {
        var origUrl = Backbone.Model.prototype.url.call(this);
        return origUrl + (origUrl.charAt(origUrl.length - 1) == '/' ? '' : '/');
    },
    defaults: function () {
        var d = new Date();
        var today = d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate();
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
        return new Date(m.get("start_date"))
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