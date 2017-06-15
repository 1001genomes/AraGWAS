import Vue from "vue";
import VueAnalytics from "vue-analytics";
import VueCharts from "vue-charts";
import VueTimeago from "vue-timeago";
import locale from "vue-timeago/locales/en-US.json";
import Vuetify from "vuetify";
import App from "./app.vue";
import router from "./router";
import introJs from "../node_modules/intro.js"

Vue.config.productionTip = false;

Vue.use(VueCharts);
Vue.use(Vuetify);

Vue.use(VueTimeago, {
  name: "timeago", // component name, `timeago` by default
  locale: "en-US",
  locales: {
    // you will need json-loader in webpack 1
    "en-US": locale,
  },
});

Vue.use(VueAnalytics, {
  id: "UA-26150757-9",
  router,
  autoTracking: {
    exception: true,
  },
});

/* eslint-disable no-new */
const app = new Vue({
  el: "#app",
  router,
  render: h => h(App),
});

import hintDirective from './directives/hint'
import introDirective from './directives/intro'

// Register the directives.
Vue.directive('hint', hintDirective);
Vue.directive('intro', introDirective);
