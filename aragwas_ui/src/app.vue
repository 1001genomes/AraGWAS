<template>
 <v-app>
    <v-toolbar class="white toolbar">
      <v-toolbar-logo class="logo aragwas-logo"><router-link :to="{name: 'home'}">Ara<b>GWAS</b>Catalog</router-link></v-toolbar-logo>
      <v-toolbar-items class="black--text">
          <v-toolbar-item class="links"><span class="black--text" @click="starttour">Take a tour?</span></v-toolbar-item>
          <v-toolbar-item class="links" id="faq-link"><router-link :to="{path: '/faq'}"><span class="black--text">FAQs</span></router-link></v-toolbar-item>
      </v-toolbar-items>
    </v-toolbar>
    <main>
      <v-container fluid class="pa-0">
        <router-view></router-view>
      </v-container>
    </main>
    <v-footer class="green" >
      <div style="width:100%;" >
          AraGWAS is a public database for <em>Arabidopsis thaliana</em> GWAS studies.
        <div class="version">
          <ul>
            <li>{{versionInfo.version}}</li>
            <li>
              <a :href="versionInfo.buildUrl" target="_blank">{{versionInfo.build}}</a>
            </li>
            <li>
              <a :href="versionInfo.githubUrl" target="_blank">{{versionInfo.githash}}</a>
            </li>
            <li><timeago :since="versionInfo.date" :auto-update="60"></timeago></li>
          </ul>
        </div>
      </div>
    </v-footer>
  </v-app>
</template>

<script lang="ts">
  import Vue from "vue";
  import Component from "vue-class-component";


  import {loadApiVersion, loadStudies} from "./api";
  import ApiVersion from "./models/apiversion";

  @Component({})
  export default class AppComponent extends Vue {
    versionInfo: ApiVersion = {} as ApiVersion;

    starttour(): void {
      this.$router.push({name:'home', query:{tour:'true'}})
    }

    async created() {
      const data: ApiVersion = await loadApiVersion();
      this.versionInfo = data;
    }
  }
</script>

<style lang="stylus">
  @import "./assets/css/main.css"
  @import "./assets/css/animate.css"
  @import "./stylus/main"
  @import "../node_modules/intro.js/introjs.css";


  #main-content {
    padding-top:0;
    background-color:transparent;
  }
  .logo a {
    color:black;
    text-decoration:none;
    font-weight:300;
  }
  .links a {
      color:black;
      text-decoration:none;
  }
  .version {
    float:right;
    font-size: 0.85rem;
    text-transform: none;
  }
  .version a {
    color:#fff;
  }
  .version ul {
    list-style: none;
    margin: 0;
    padding: 0;

  }
  .version ul li {
    display: inline-block;
    padding: 2px;
  }

</style>
