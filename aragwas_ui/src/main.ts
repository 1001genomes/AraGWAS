import Vue from 'vue';
import Vuetify from 'vuetify';
import App from './app.vue';
import router from './router';

import VueCharts from 'vue-charts';

Vue.config.productionTip = false;

Vue.use(VueCharts);
Vue.use(Vuetify);

/* eslint-disable no-new */
const app = new Vue({
  el: '#app',
  router,
  render: h => h(App),
});
