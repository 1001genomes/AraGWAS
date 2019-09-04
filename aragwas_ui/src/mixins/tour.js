import _ from "lodash";
import introJs from "intro.js";


const tourMixin = {
    mounted() {
        this.checkTour();
    },
    watch: {
        $route(val, oldVal) {
            if (val.query.tour) {
                this.checkTour();
            }
        }
    },
    methods: {
        checkTour() {
             if (this.$route.query.tour && this.tourOptions) {
                const intro = introJs.introJs();
                if (this.tourOptions.callback) {
                    var callback = this.tourOptions.callback;
                    var component = this;
                    intro.onchange(function() {
                        callback(this, component);
                    });
                }
                const doneLabel = this.tourOptions.nextPage ? "Next Page" : "Done";
                const view = this.$route.name;
                const nextPage = this.tourOptions.nextPage;
                let isFinished = false;
                intro.setOptions({doneLabel: doneLabel, steps: this.tourOptions.steps});
                this.$nextTick(() => {
                    this.$ga.event("Tour", "start", view);
                    intro.start().oncomplete(() => {
                        if (nextPage) {
                            this.$ga.event("Tour", "nextpage", view);
                            this.$router.push(_.assign(this.tourOptions.nextPage, {query: {tour: "1"}}));
                        } else {
                            this.$ga.event("Tour", "finish", view);
                        }
                        isFinished = true;
                    }).onexit(() => {
                        if (!isFinished || !nextPage) {
                            this.$router.replace({query: {}});
                            if (!isFinished) {
                                this.$ga.event("Tour", "abort", view);
                            }
                        }
                    });
                });
            }
        },
    },
};

export default tourMixin;
