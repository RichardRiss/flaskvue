// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import 'tailwindcss/tailwind.css'
import VueTailwind from 'vue-tailwind'
import settings from './assets/tailwindsettings.js'
import VueSocketIO from 'vue-socket.io'
import SocketIO from 'socket.io-client'

Vue.use(VueTailwind, settings)

Vue.use(
  new VueSocketIO({
    debug: true,
    connection: SocketIO('http://localhost:5000')// document.location.href   -> change back for prod
  })
)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
