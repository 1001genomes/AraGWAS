const intro = require('intro.js');

const hintDirective = {

    bind: function() {

        const name = this.arg;
        const viewModel = this.vm;
        const tours = viewModel.$intro;

        if (!tours.hasOwnProperty(name)) {

            var options = tours._defaultOptions;
            var tour = tours[name] = intro.introJs();

            // Setup the tour hooks.
            this.setupHooks(tour);

            // Set the tour options.
            tour.setOptions(options);
        }
    },

    setupHooks: function(tour) {

        const viewModel = this.vm;

        tour.onhintclick(function() {
            viewModel.$dispatch('hint:click', arguments);
        });

        tour.onhintsadded(function() {
            viewModel.$dispatch('hint:added', arguments);
        });

        tour.onhintclose(function() {
            viewModel.$dispatch('hint:close', arguments);
        });
    },

    update: function(newValue, oldValue) {

        const name = this.arg;
        const element = this.el;
        const viewModel = this.vm;
        const tours = viewModel.$intro;
        const hint = Object.assign({}, newValue, {element: element});

        if (!tours[name]._options.hasOwnProperty('hints')) {
            tours[name]._options.hints = [];
        }

        tours[name]._options.hints.push(hint);
        tours[name].refresh();
    },

    unbind: function() {

        const name = this.arg;
        const viewModel = this.vm;
        const tours = viewModel.$intro;

        if (tours.hasOwnProperty(name)) {
            delete tours[name];
        }
    }
};

module.exports = hintDirective;
