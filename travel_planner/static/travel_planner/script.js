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
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function setupCSRFToken() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}
setupCSRFToken();
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
    showSave: false,
    template: _.template($('#trip-card-template').html()),
    initialize: function () {
        this.listenTo(this.model, 'change', this.render);
        this.listenTo(this.model, 'destroy', this.remove);
        this.listenTo(this.model, 'sync', this.showSaved);
        this.listenTo(this.model, 'hideThisItem', function () {
            this.$el.hide();
        });
        this.listenTo(this.model, 'showThisItem', function () {
            this.$el.show();
        });
    },
    events: {
        'click .remove-dest': function (e) {
            var view = this;
            this.$el.slideUp(150, function () {
                view.model.destroy();
            });
            e.preventDefault();
        },
        'keypress input[name=destination]': function (e) {
            if (e.keyCode == 13) e.target.blur();
        },
        'blur input[name=destination],textarea': 'edit',
        'keydown input,textarea': 'show_save',
        'click input.save-dest': function (e) {
            e.preventDefault();
        },
        'hide .datepicker': 'date_edit',
        'show .datepicker': 'show_save'
    },
    show_save: function (e) {
        if (e.target.name != "save") {
            this.$saveDest.fadeIn(100);
        }
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
        if (e.target.value != this.model.get(e.target.name))
            this.model.save(save_value);
        else
            this.$saveDest.fadeOut(100);
    },
    showSaved: function () {
        var $saveDest = this.$saveDest;
        this.$saveDest.fadeIn(0);
        $saveDest.val("Saved");
        $saveDest.fadeOut(400, function () {
            $saveDest.val("Save")
        });
    },
    render: function () {
        this.$el.html(this.template(this.model.toJSON()));
        this.$el.find(".datepicker").datepicker();
        this.$saveDest = this.$el.find(".save-dest");
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

function showAll() {
    trips.each(function (item) {
        item.trigger("showThisItem")
    });
}

function tripsShowElseHide(func) {
    trips.each(function (trip) {
        var start_date = get_date_only(trip.get("start_date"));
        if (func(trip)) {
            trip.trigger("showThisItem");
        } else {
            trip.trigger("hideThisItem");
        }
    });
}

function handleSelectFilter($this) {
    var today = get_date_only(dateToDateString(new Date()));
    var d = new Date();
    if ($this.hasClass("show-all")) {
        showAll();
    } else if ($this.hasClass("next-month")) {
        d.setMonth(d.getMonth() + 1);
        var nextMonthDate = get_date_only(dateToDateString(d));
        tripsShowElseHide(function (trip) {
            var end_date = get_date_only(trip.get("end_date"));
            return end_date > today && end_date < nextMonthDate;
        });
    } else if ($this.hasClass("next-year")) {
        d.setFullYear(d.getFullYear() + 1);
        var nextYearDate = get_date_only(dateToDateString(d));
        tripsShowElseHide(function (trip) {
            var end_date = get_date_only(trip.get("end_date"));
            return end_date > today && end_date < nextYearDate;
        });
    } else if ($this.hasClass("past")) {
        tripsShowElseHide(function (trip) {
            var end_date = get_date_only(trip.get("end_date"));
            return end_date < today;
        });
    }
}

function prepareSearch($filterBar) {
    $filterBar.show();
    $filterBar.find(".nav-link").click(function () {
        $filterBar.find(".nav-item").removeClass("active");
        var $this = $(this);
        $this.parent().addClass("active");
        handleSelectFilter($this)
    });
    var $searchBox = $filterBar.find(".search-destinations");
    $filterBar.find(".search-destinations-button").click(function (e) {
        e.preventDefault();
    });
    $searchBox.keyup(function () {
        $filterBar.find(".nav-link.show-all").click();
        tripsShowElseHide(function (item) {
            return item.get("destination").toLowerCase().startsWith($searchBox.val().toLowerCase());
        });
    });
}

function preparePrintButton($filterBar, $printPlan) {
    $printPlan.click(function (e) {
        e.preventDefault();
        $filterBar.find(".nav-link.next-month").click();
        window.print();
    })
}

function prepareLogin($loginMenu, $loginForm, $userInfo, $tripList) {
    $loginForm.submit(function (e) {
        e.preventDefault();
        $loginForm.find("input[type=submit]").val("Logging in...");
        var username = $loginForm.find("input[name=username]").val();
        $.post(
            $loginForm.find("#ajax_login").val(),
            {
                username: username,
                password: $loginForm.find("input[name=password]").val(),
                time_zone: -(new Date().getTimezoneOffset() / 60)
            },
            function (data) {
                $loginMenu.hide();
                $userInfo.show();
                $("#username-field").html(username);
                $tripList.show();
                setupCSRFToken();
                trips.fetch();
                // Cleanup login form in case user wants to log in again
                $loginForm.find("input[name=username]").val("");
                $loginForm.find("input[name=password]").val("");
                $loginForm.find("input[type=submit]").val("Login");
                $loginForm.find(".login-error-message").hide();
            }
        ).fail(function (xhr, status, error) {
            $loginForm.find(".login-error-message").show();
            if (xhr.responseText)
                $loginForm.find(".login-error-message").html(xhr.responseText);
            else if (xhr.status == 0)
                $loginForm.find(".login-error-message").html("Couldn't communicate with server.");
            else
                $loginForm.find(".login-error-message").html(xhr.statusText);
            $loginForm.find("input[type=submit]").val("Login");
        });

    });
}

function prepareLogout($loginMenu, $userInfo, $tripList) {
    var $logoutButton = $userInfo.find(".logout-button");
    $logoutButton.click(function (e) {
        e.preventDefault();
        $.get($logoutButton.attr("href"), function () {
            trips.reset([]);
            $loginMenu.show();
            $userInfo.hide();
            $("#username-field").html("");
            $tripList.hide();
            setupCSRFToken();
        });
    });
}

function prepareRegistration($loginMenu, $registerForm, $userInfo, $tripList) {
    $registerForm.submit(function (e) {
        e.preventDefault();
        var username = $registerForm.find("input[name=username]").val();
        var password = $registerForm.find("input[name=password]").val();
        var passwordConfirm = $registerForm.find("input[name=password-confirm]").val();
        var errorBox = $registerForm.find('.register-error-message');
        if (password != passwordConfirm) {
            errorBox.show();
            errorBox.html("Passwords do not match");
            return;
        }

        $.post(
            $registerForm.attr("action"),
            {
                username: username,
                password: $registerForm.find("input[name=password]").val(),
                time_zone: -(Math.floor(new Date().getTimezoneOffset() / 60))
            },
            function (data) {
                $loginMenu.hide();
                $userInfo.show();
                $("#username-field").html(username);
                $tripList.show();
                setupCSRFToken();
                trips.fetch();
                // Cleanup registration form in case user wants to log in again
                errorBox.hide();
                $registerForm.find("input[name=username]").val("");
                $registerForm.find("input[name=password]").val("");
                $registerForm.find("input[name=password-confirm]").val("");
                $registerForm.find("input[type=submit]").val("Register");
            }
        ).fail(function (xhr, status, error) {
            $registerForm.find("input[type=submit]").val("Register");
            errorBox.show();
            if (xhr.status == 0)
                errorBox.html("Couldn't communicate with server.");
            else if (xhr.status == 409)
                errorBox.html("That username is already being used.");
            else if (xhr.responseText)
                errorBox.html(xhr.responseText);
            else
                errorBox.html(xhr.statusText);
        });
    });
}

$(function () {
    var app = new AppView();
    $(".add-dest").click(function (e) {
        trips.create();
        e.preventDefault();
    });

    var $loginMenu = $("#login-menu");
    var $loginForm = $("#login-form");
    var $registerForm = $("#register-form");
    var $userInfo = $("#user-info");
    var $tripList = $("#trip-list");
    prepareLogin($loginMenu, $loginForm, $userInfo, $tripList);
    prepareLogout($loginMenu, $userInfo, $tripList);
    prepareRegistration($loginMenu, $registerForm, $userInfo, $tripList);
    var $filterBar = $('.filter-bar');
    prepareSearch($filterBar);
    var $printPlan = $(".print-plan");
    preparePrintButton($filterBar, $printPlan);

    $registerForm.submit(function (e) {
        e.preventDefault();
    });

    if ($loginMenu.is(':visible')) {
    } else {
        trips.fetch();
    }
});