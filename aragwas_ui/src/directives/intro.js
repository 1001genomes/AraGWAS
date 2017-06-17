import intro from "intro.js";

const introDirective = {

    bind: function() {

        const name = this.arg;
        const viewModel = this.vm;
        const element = this.vm.$el;
        const tours = viewModel.$intro;
        this.vm.$el.style += "color: white";

        if (!tours.hasOwnProperty(name)) {

            var options = tours._defaultOptions;
            var tour = tours[name] = intro.introJs(element);

            // Setup the tour hooks.
            this.setupHooks(tour);

            // Set the tour options.
            tour.setOptions(options);
        }
    },

    setupHooks: function(tour) {

        const name = this.arg;
        const viewModel = this.vm;

        tour.oncomplete(function() {
            viewModel.$dispatch('tour:complete', name);
        });

        tour.onexit(function() {
            viewModel.$dispatch('tour:exit', name);
        });

        tour.onchange(function() {
            viewModel.$dispatch('tour:change', arguments);
        });

        tour.onbeforechange(function() {
            viewModel.$dispatch('tour:beforeChange', arguments);
        });

        tour.onafterchange(function() {
            viewModel.$dispatch('tour:afterChange', arguments);
        });
    },

    update: function(newValue, oldValue) {

        const name = this.arg;
        const element = this.el;
        const viewModel = this.vm;
        const tours = viewModel.$intro;
        const step = Object.assign({}, newValue, {element: element});

        if (!tours[name]._options.hasOwnProperty('steps')) {
            tours[name]._options.steps = [];
        }

        tours[name]._options.steps.push(step);
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

export default introDirective;
