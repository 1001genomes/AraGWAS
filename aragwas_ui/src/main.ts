import Vue from 'vue';
import VueCharts from 'vue-charts';
import VueTimeago from 'vue-timeago';
import locale from 'vue-timeago/locales/en-US.json';
import Vuetify from 'vuetify';
import App from './app.vue';
import router from './router';

Vue.config.productionTip = false;

Vue.use(VueCharts);
Vue.use(Vuetify);

Vue.use(VueTimeago, {
  name: 'timeago', // component name, `timeago` by default
  locale: 'en-US',
  locales: {
    // you will need json-loader in webpack 1
    'en-US': locale,
  },
});

/* eslint-disable no-new */
const app = new Vue({
  el: '#app',
  router,
  render: h => h(App),
});
