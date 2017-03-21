import Vue from 'vue'
import Vuetify from 'vuetify'
import router from "./router";
import App from './app'

Vue.config.productionTip = false

Vue.use(Vuetify)

/* eslint-disable no-new */
new Vue({
  el: "#app",
  router,
  render: h => h(App)
});
